"""Native managed-install retry and real neural HTTP verification, in isolated storage."""

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def run_setup(bundle: Path, storage: Path, model: Path, version: str, log: Path) -> tuple[int, list[dict]]:
    records = []
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    with log.open("a", encoding="utf-8") as output:
        process = subprocess.Popen([sys.executable, str(bundle / "scripts/install_backend.py"),
            "--bundle", str(bundle), "--storage", str(storage), "--version", version, "--model-file", str(model)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            creationflags=flags, env={**os.environ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"})
        try:
            for line in process.stdout:
                output.write(line); output.flush()
                if line.startswith(("TOKENWISE_PROGRESS ", "TOKENWISE_SETUP_ERROR ")):
                    item = json.loads(line.split(" ", 1)[1]); records.append(item)
                    print(f"Step {item.get('step', '?')}/7: {item.get('message', '')}", flush=True)
            return process.wait(), records
        finally:
            if process.poll() is None:
                process.terminate(); process.wait(timeout=20)
            process.stdout.close()


def request(url: str, payload: dict | None = None, timeout: float = 120) -> dict:
    call = Request(url, data=json.dumps(payload).encode("utf-8") if payload is not None else None,
                   headers={"Content-Type": "application/json"})
    with urlopen(call, timeout=timeout) as response:
        return json.load(response)


def verify(bundle: Path, model: Path, version: str, root: Path) -> dict:
    storage = root / "storage"
    invalid = root / "invalid-model.safetensors"
    invalid.write_bytes(b"deliberately invalid verifier fixture")
    log = root / "setup.log"
    print("Installing real CPU dependencies; then deliberately failing model verification.", flush=True)
    code, records = run_setup(bundle, storage, invalid, version, log)
    if code != 1 or not any(item.get("stage") == "model" and "hint" in item for item in records):
        raise RuntimeError("Expected a recoverable model-step failure.\n" + log.read_text(encoding="utf-8")[-4000:])
    print("Retrying with verified local weights; successful dependency steps must be reused.", flush=True)
    code, records = run_setup(bundle, storage, model, version, log)
    if code or sum(item.get("message") == "Completed dependency step verified and reused" for item in records) != 3:
        raise RuntimeError("Setup retry did not reuse its three dependency checkpoints.\n" + log.read_text(encoding="utf-8")[-4000:])
    installation = Path(next(item["installation_root"] for item in records if item["stage"] == "complete"))
    assert installation.resolve().is_relative_to(storage.resolve())
    python = installation / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
    source = installation / "swe-pruner/swe-pruner"
    workspace = root / "Python Repository"
    (workspace / "services").mkdir(parents=True)
    (workspace / "tests").mkdir()
    filename = workspace / "services/auth.py"
    text = "LOCKOUT_THRESHOLD = 3\n\ndef is_locked(failed_attempts):\n    return failed_attempts >= LOCKOUT_THRESHOLD\n"
    filename.write_text(text, encoding="utf-8")
    (workspace / "tests/test_auth.py").write_text("from services.auth import is_locked\n\ndef test_account_lockout():\n    assert is_locked(3)\n    assert not is_locked(2)\n", encoding="utf-8")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1", "PYTHONPATH": str(source / "src"),
                   "SWEPRUNER_MODEL_PATH": str(source / "model"), "SWEPRUNER_CARBON_ARTIFACTS_DIR": str(source / "carbon_artifacts"),
                   "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    with (root / "backend.log").open("w", encoding="utf-8") as output:
        process = subprocess.Popen([str(python), "-m", "uvicorn", "swe_pruner.online_serving:app", "--host", "127.0.0.1", "--port", str(port)],
                                   cwd=installation, env=environment, stdout=output, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            print("Starting the isolated backend with real pinned neural weights.", flush=True)
            deadline = time.monotonic() + 90
            health = {}
            while time.monotonic() < deadline and process.poll() is None:
                try:
                    health = request(base + "/health", timeout=1)
                    if health.get("model_loaded"):
                        break
                except (URLError, TimeoutError):
                    pass
                time.sleep(0.3)
            assert health.get("model_loaded") and health.get("repository_indexing")
            assert Path(health["model_path"]).resolve() == (source / "model").resolve()
            index = {"workspace_root": str(workspace), "watcher_id": "native-smoke", "action": "start", "sequence": 1}
            first_index = request(base + "/index-workspace", index)
            assert first_index["indexed_files"] == 2
            query = {"workspace_root": str(workspace), "query": "Explain LOCKOUT_THRESHOLD account lockout and its related tests", "token_budget": 2048}
            began = time.perf_counter()
            first = request(base + "/prune-workspace", query)
            retrieval_ms = round((time.perf_counter() - began) * 1000, 2)
            assert first["index_cache_hit"] and first["retrieval_cache_hit"] and first["files"]
            assert 0 < first["pruned_tokens"] <= 2048
            assert request(base + "/prune-workspace", query)["context_cache_hit"]
            filename.write_text(text.replace("= 3", "= 5"), encoding="utf-8")
            updated = request(base + "/index-workspace", {**index, "action": "update", "sequence": 2, "paths": ["services/auth.py"]})
            assert updated["repository_fingerprint"] != first_index["repository_fingerprint"]
            changed = request(base + "/prune-workspace", query)
            assert not changed["context_cache_hit"] and "LOCKOUT_THRESHOLD = 5" in changed["unified_prompt"]
            assert changed["pruned_tokens"] <= 2048
            request(base + "/index-workspace", {**index, "action": "stop", "sequence": 3})
            return {"fresh_dependencies_installed": True, "recovered_failed_step": 5, "dependency_steps_reused": 3,
                    "real_model_loaded": True, "indexed_files": 2, "token_budget": 2048, "cache_invalidation_verified": True,
                    "first_neural_retrieval_ms": retrieval_ms, "antigravity_cloud_called": False}
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                else:
                    process.terminate()
            process.wait(timeout=20)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-file", type=Path, default=ROOT / "swe-pruner/swe-pruner/model/model.safetensors")
    args = parser.parse_args()
    model = args.model_file.resolve()
    if not model.is_file():
        parser.error("Provide checksum-verifiable pinned model weights with --model-file.")
    version = json.loads((ROOT / "vscode-extension/package.json").read_text(encoding="utf-8"))["version"]
    releases = (ROOT / "releases").resolve()
    releases.mkdir(exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=".tokenwise-managed-smoke-", dir=releases)).resolve()
    assert root.parent == releases and root.name.startswith(".tokenwise-managed-smoke-")
    verification_failed = False
    try:
        result = verify(ROOT / "vscode-extension/resources/backend-bundle", model, version, root)
        print(json.dumps(result, indent=2), flush=True)
    except Exception:
        verification_failed = True
        for filename in ("setup.log", "backend.log"):
            log = root / filename
            if log.is_file():
                print(f"{filename}:\n{log.read_text(encoding='utf-8')[-4000:]}", file=sys.stderr)
        raise
    finally:
        # Windows can release mapped Python DLLs shortly after taskkill returns.
        for attempt in range(20):
            try:
                shutil.rmtree(root)
                break
            except OSError:
                if attempt == 19:
                    if verification_failed:
                        print(f"Could not remove isolated verification storage: {root}", file=sys.stderr)
                        break
                    raise
                time.sleep(1)
    print("Isolated backend stopped and temporary managed storage removed.")


if __name__ == "__main__":
    main()
