"""Antigravity PreInvocation adapter. Keep stdout exclusively for the hook JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


MARKER = "[TokenWise automatic context]"
DEFAULTS = {
    "enabled": True, "token_budget": 4096, "threshold": 0.45, "max_candidates": 6,
    "backend_port": 8000, "auto_start_backend": True,
    "startup_timeout_seconds": 40, "request_timeout_seconds": 90,
}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=True, indent=2)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def reverse_lines(path: Path, max_bytes: int = 16 * 1024 * 1024) -> Iterator[str]:
    """Find recent user turns without loading a potentially large tool transcript."""
    with path.open("rb") as stream:
        position = stream.seek(0, os.SEEK_END)
        minimum = max(0, position - max_bytes)
        remainder = b""
        while position > minimum:
            size = min(65536, position - minimum)
            position -= size
            stream.seek(position)
            pieces = (stream.read(size) + remainder).split(b"\n")
            remainder = pieces[0]
            for line in reversed(pieces[1:]):
                if line.strip():
                    yield line.decode("utf-8", errors="replace")
        if minimum == 0 and remainder.strip():
            yield remainder.decode("utf-8", errors="replace")


def message_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n".join(
            str(part.get("text", "")) for part in content if isinstance(part, dict)
        ).strip()
    return ""


def latest_prompt(payload: dict) -> tuple[str, str] | None:
    transcript = payload.get("transcriptPath")
    if not transcript:
        return None
    for line in reverse_lines(Path(transcript).expanduser()):
        try:
            record = json.loads(line)
        except ValueError:
            continue  # Antigravity may still be writing the trailing record.
        if not isinstance(record, dict):
            continue
        # Explicit Antigravity user records, plus standard role-based transcripts.
        explicit = record.get("type") == "USER_INPUT" and record.get("source") == "USER_EXPLICIT"
        standard = record.get("role") == "user" and "type" not in record
        if not (explicit or standard):
            continue
        query = message_text(record.get("content"))
        if not query or query.startswith(MARKER):
            continue
        identity = json.dumps([
            payload.get("conversationId"), record.get("step_index", record.get("id")),
            record.get("created_at", record.get("timestamp")), query,
        ], ensure_ascii=True)
        return query, hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return None


@contextmanager
def file_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    try:
        try:
            if path.exists() and time.time() - path.stat().st_mtime > 180:
                path.unlink(missing_ok=True)
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(descriptor)
            acquired = True
        except FileExistsError:
            pass
        yield acquired
    finally:
        if acquired:
            path.unlink(missing_ok=True)


def request_json(url: str, payload: dict | None = None, timeout: float = 2) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"},
    )
    # Local requests must not pass through a machine's HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"TokenWise HTTP {exc.code}: {detail}") from exc


def health(port: int) -> dict | None:
    try:
        result = request_json(f"http://127.0.0.1:{port}/health", timeout=0.8)
        return result if result.get("service") == "tokenwise" else None
    except (OSError, ValueError, RuntimeError):
        return None


def ensure_backend(project_root: Path, settings: dict) -> str:
    runtime = project_root / ".tokenwise"
    runtime.mkdir(exist_ok=True)
    registration = read_json(runtime / "backend.json")
    preferred = int(settings["backend_port"])
    remembered = registration.get("port", preferred)
    port = remembered if isinstance(remembered, int) and 1024 <= remembered <= 65535 else preferred
    status = health(port)
    if status:
        if not status.get("model_loaded"):
            raise RuntimeError("TokenWise is running but its model is not loaded. Check .tokenwise/backend.log.")
        return f"http://127.0.0.1:{port}"
    if not settings["auto_start_backend"]:
        raise RuntimeError("TokenWise backend is offline and automatic startup is disabled.")
    if not (project_root / "swe-pruner/swe-pruner/model/model.safetensors").is_file():
        raise RuntimeError("Pruning weights are missing. Run scripts/copy-model.ps1 before using TokenWise.")

    deadline = time.monotonic() + float(settings["startup_timeout_seconds"])
    with file_lock(runtime / "backend-start.lock") as acquired:
        if acquired:
            # Another conversation may have finished starting the service while we acquired the lock.
            registration = read_json(runtime / "backend.json")
            port = registration.get("port", preferred)
            if not health(port):
                for candidate in range(preferred, min(preferred + 10, 65536)):
                    with socket.socket() as probe:
                        try:
                            probe.bind(("127.0.0.1", candidate))
                        except OSError:
                            continue
                    port = candidate
                    break
                else:
                    raise RuntimeError("No free local port is available for TokenWise.")
                environment = os.environ.copy()
                environment.update({
                    "SWEPRUNER_MODEL_PATH": str(project_root / "swe-pruner/swe-pruner/model"),
                    "SWEPRUNER_CARBON_ARTIFACTS_DIR": str(project_root / "swe-pruner/swe-pruner/carbon_artifacts"),
                    "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "PYTHONUTF8": "1",
                    "PYTHONPATH": str(project_root / "swe-pruner/swe-pruner/src"),
                })
                flags = (subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS) if os.name == "nt" else 0
                with (runtime / "backend.log").open("ab") as log:
                    process = subprocess.Popen(
                        [sys.executable, "-m", "uvicorn", "swe_pruner.online_serving:app",
                         "--host", "127.0.0.1", "--port", str(port)],
                        cwd=project_root, env=environment, stdin=subprocess.DEVNULL,
                        stdout=log, stderr=log, creationflags=flags, start_new_session=os.name != "nt",
                    )
                write_json(runtime / "backend.json", {
                    "pid": process.pid, "port": port, "project_root": str(project_root),
                })
        while time.monotonic() < deadline:
            registration = read_json(runtime / "backend.json")
            port = registration.get("port", port)
            status = health(port)
            if status:
                if not status.get("model_loaded"):
                    raise RuntimeError("TokenWise could not load its model. Check .tokenwise/backend.log.")
                return f"http://127.0.0.1:{port}"
            time.sleep(0.3)
    raise RuntimeError("TokenWise startup timed out. See .tokenwise/backend.log; Antigravity can continue normally.")


def load_settings(workspace: Path) -> dict:
    path = workspace / ".agents/tokenwise.json"
    overrides = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    if not isinstance(overrides, dict):
        raise ValueError("TokenWise settings must be a JSON object")
    settings = {**DEFAULTS, **overrides}
    for key in ("enabled", "auto_start_backend"):
        if not isinstance(settings[key], bool):
            raise ValueError(f"TokenWise setting {key} must be a boolean")
    bounds = {
        "token_budget": (256, 32768), "threshold": (0, 1), "max_candidates": (1, 32),
        "backend_port": (1024, 65525), "startup_timeout_seconds": (1, 60),
        "request_timeout_seconds": (1, 120),
    }
    for key, (minimum, maximum) in bounds.items():
        value = settings[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= value <= maximum:
            raise ValueError(f"Invalid TokenWise setting: {key}")
        if key not in {"threshold", "startup_timeout_seconds", "request_timeout_seconds"} and not isinstance(value, int):
            raise ValueError(f"TokenWise setting {key} must be an integer")
    return settings


def retrieve_context(project_root: Path, workspace: Path, query: str, settings: dict) -> tuple[str, dict]:
    base_url = ensure_backend(project_root, settings)
    result = request_json(f"{base_url}/prune-workspace", {
        "query": query, "workspace_root": str(workspace),
        "token_budget": settings["token_budget"], "threshold": settings["threshold"],
        "max_candidates": settings["max_candidates"],
    }, timeout=float(settings["request_timeout_seconds"]))
    if not result.get("files") or not result.get("unified_prompt", "").startswith(MARKER):
        raise RuntimeError("TokenWise returned no usable automatic repository context.")
    tokens = result.get("pruned_tokens")
    if isinstance(tokens, bool) or not isinstance(tokens, int) or not 0 <= tokens <= settings["token_budget"]:
        raise RuntimeError("TokenWise context exceeded its configured token budget or has an invalid token count.")
    return base_url, result


def run_hook(payload: dict, project_root: Path, workspace: Path) -> dict:
    started = time.monotonic()
    runtime = workspace / ".tokenwise"
    event = {
        "event_id": uuid.uuid4().hex, "timestamp": datetime.now(timezone.utc).isoformat(),
        "transport": "antigravity-hook", "status": "retrieving",
        "verification": payload.get("tokenwiseVerification") is True
        or str(payload.get("conversationId", "")).startswith("tokenwise-verification-"),
    }
    try:
        settings = load_settings(workspace)
        if not settings["enabled"]:
            return {}
        if not workspace.is_dir():
            raise ValueError("The TokenWise workspace does not exist.")
        mounted = payload.get("workspacePaths", [])
        if mounted and workspace not in [Path(path).resolve() for path in mounted]:
            return {}
        prompt = latest_prompt(payload)
        if prompt is None:
            raise ValueError("No explicit user prompt was found in Antigravity's transcript.")
        query, prompt_id = prompt
        event.update({"query": query, "prompt_id": prompt_id})
        conversation = str(payload.get("conversationId", "default"))
        state_name = hashlib.sha256(conversation.encode("utf-8")).hexdigest()
        state_path = runtime / "conversations" / f"{state_name}.json"
        with file_lock(state_path.with_suffix(".lock")) as acquired:
            if not acquired:
                return {}
            previous = read_json(state_path)
            if previous.get("prompt_id") == prompt_id:
                return {}
            write_json(runtime / "latest.json", event)
            base_url, result = retrieve_context(project_root, workspace, query, settings)
            event.update({
                "status": "ready", "result": result, "backend_url": base_url,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            })
            write_json(runtime / "latest.json", event)
            write_json(state_path, {"prompt_id": prompt_id, "event_id": event["event_id"]})
            # userMessage keeps repository text at user priority and persists it for later tool steps.
            return {"injectSteps": [{"userMessage": result["unified_prompt"]}]}
    except Exception as exc:
        event.update({"status": "error", "error": str(exc)})
        try:
            write_json(runtime / "latest.json", event)
        except OSError:
            pass
        print(f"TokenWise: {exc}", file=sys.stderr)
        return {}


def main(project_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Hook input must be a JSON object")
        root = project_root or Path(__file__).resolve().parents[4]
        response = run_hook(payload, root, args.workspace.resolve())
    except Exception as exc:
        print(f"TokenWise: {exc}", file=sys.stderr)
        response = {}
    print(json.dumps(response, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
