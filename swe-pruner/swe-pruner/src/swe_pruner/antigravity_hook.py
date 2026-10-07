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
from .conversation_context import conversation_hint, next_user_turns


MARKER = "[TokenWise automatic context]"
DEFAULTS = {
    "enabled": True, "token_budget": 4096, "threshold": 0.45, "max_candidates": 6,
    "response_guidance": True,
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
        if record.get("conversationId") is not None and payload.get("conversationId") is not None \
                and record["conversationId"] != payload["conversationId"]:
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


def backend_runtime_directory(project_root: Path) -> Path:
    configured = os.environ.get("TOKENWISE_RUNTIME_DIR")
    if not configured:
        return project_root / ".tokenwise"
    runtime = Path(configured).expanduser()
    if not runtime.is_absolute():
        raise ValueError("TOKENWISE_RUNTIME_DIR must be an absolute directory path.")
    return runtime.resolve()


def registered_port(registration: dict, project_root: Path) -> int | None:
    port = registration.get("port")
    root = registration.get("project_root")
    if type(port) is not int or not 1024 <= port <= 65535 or not isinstance(root, str):
        return None
    return port if Path(root).resolve() == project_root else None


def matching_backend(port: int, model_path: Path, log_path: Path) -> dict | None:
    status = health(port)
    if not status or not isinstance(status.get("model_path"), str):
        return None
    if Path(status["model_path"]).resolve() != model_path:
        return None
    if not status.get("model_loaded"):
        raise RuntimeError(f"TokenWise is running but its model is not loaded. Check {log_path}.")
    return status


def ensure_backend(project_root: Path, settings: dict) -> str:
    project_root = project_root.resolve()
    runtime = backend_runtime_directory(project_root)
    runtime.mkdir(parents=True, exist_ok=True)
    preferred = int(settings["backend_port"])
    model_path = (project_root / "swe-pruner/swe-pruner/model").resolve()
    log_path = runtime / "backend.log"

    def reuse_running() -> int | None:
        # Adopt a healthy checkout-era process instead of loading a second copy of the model.
        records = [read_json(runtime / "backend.json")]
        if runtime != project_root / ".tokenwise":
            records.append(read_json(project_root / ".tokenwise/backend.json"))
        candidates = [(registered_port(record, project_root), record) for record in records]
        candidates.append((preferred, {}))
        checked = set()
        for candidate, record in candidates:
            if candidate is None or candidate in checked:
                continue
            checked.add(candidate)
            status = matching_backend(candidate, model_path, log_path)
            if status:
                registration = {"port": candidate, "project_root": str(project_root)}
                pid = status.get("pid", record.get("pid"))
                if type(pid) is int and pid > 0:
                    registration["pid"] = pid
                if read_json(runtime / "backend.json") != registration:
                    write_json(runtime / "backend.json", registration)
                return candidate
        return None

    port = reuse_running()
    if port is not None:
        return f"http://127.0.0.1:{port}"
    if not settings["auto_start_backend"]:
        raise RuntimeError("TokenWise backend is offline and automatic startup is disabled.")
    if not (project_root / "swe-pruner/swe-pruner/model/model.safetensors").is_file():
        raise RuntimeError("Pruning weights are missing. Run scripts/copy-model.ps1 before using TokenWise.")

    deadline = time.monotonic() + float(settings["startup_timeout_seconds"])
    with file_lock(runtime / "backend-start.lock") as acquired:
        if acquired:
            # Another conversation may have finished starting the service while we acquired the lock.
            port = reuse_running()
            if port is None:
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
                with log_path.open("ab") as log:
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
            port = registered_port(registration, project_root)
            status = matching_backend(port, model_path, log_path) if port is not None else None
            if status:
                return f"http://127.0.0.1:{port}"
            time.sleep(0.3)
    raise RuntimeError(f"TokenWise startup timed out. See {log_path}; Antigravity can continue normally.")


def load_settings(workspace: Path) -> dict:
    path = workspace / ".agents/tokenwise.json"
    overrides = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    if not isinstance(overrides, dict):
        raise ValueError("TokenWise settings must be a JSON object")
    settings = {**DEFAULTS, **overrides}
    for key in ("enabled", "auto_start_backend", "response_guidance"):
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


def retrieve_context(project_root: Path, workspace: Path, query: str, settings: dict, context_hint: str = "") -> tuple[str, dict]:
    base_url = ensure_backend(project_root, settings)
    result = request_json(f"{base_url}/prune-workspace", {
        "query": query, "workspace_root": str(workspace),
        "token_budget": settings["token_budget"], "threshold": settings["threshold"],
        "max_candidates": settings["max_candidates"],
        "response_guidance": settings["response_guidance"],
        **({"context_hint": context_hint} if context_hint else {}),
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
            scoped = isinstance(payload.get("conversationId"), str) and bool(payload["conversationId"].strip())
            hint = conversation_hint(query, previous, scoped)
            base_url, result = retrieve_context(project_root, workspace, query, settings, hint)
            if isinstance(result.get("input_trace"), dict):
                result["input_trace"]["history_source"] = "native_scoped_user_turns" if hint else "none"
            event.update({
                "status": "ready", "result": result, "backend_url": base_url,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            })
            write_json(runtime / "latest.json", event)
            turns = next_user_turns(query, previous, scoped)
            write_json(state_path, {"prompt_id": prompt_id, "event_id": event["event_id"],
                                    "topic_query": turns[0] if turns else "", "user_turns": turns})
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
