"""Verify overview retrieval and extension carbon mapping against an isolated real backend."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "swe-pruner/swe-pruner"


@contextmanager
def isolated_directory(scratch: Path):
    temporary = tempfile.TemporaryDirectory(prefix="context-results-", dir=scratch)
    try:
        yield Path(temporary.name).resolve()
    finally:
        # Windows can retain mapped handles briefly after the child interpreter exits.
        for attempt in range(20):
            try:
                temporary.cleanup()
                break
            except OSError:
                if attempt == 19:
                    raise
                time.sleep(.5)


def request(base: str, endpoint: str, payload: dict | None = None) -> dict:
    call = Request(base + endpoint,
                   data=json.dumps(payload).encode("utf-8") if payload is not None else None,
                   headers={"Content-Type": "application/json"})
    with urlopen(call, timeout=120) as response:
        return json.load(response)


def write_fixture(root: Path, name: str, text: str) -> None:
    filename = root / name
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(text, encoding="utf-8")


def carbon_comparison(base: str, result: dict) -> dict:
    # Exercise the compiled extension client and mapper, not a Python approximation of them.
    payload = {"base": base, "before": result["raw_context_tokens"], "after": result["pruned_tokens"]}
    completed = subprocess.run(["node", str(ROOT / "scripts/verify-carbon-client.cjs")],
                               input=json.dumps(payload), cwd=ROOT,
                               capture_output=True, text=True, encoding="utf-8", timeout=40, check=True)
    carbon = json.loads(completed.stdout)
    assert carbon["carbonStatus"] == "ready"
    assert carbon["carbonBaseline"] == "formatted-context"
    assert carbon["carbonBefore"]["co2Grams"] > 0
    assert carbon["carbonAfter"]["co2Grams"] > 0
    return carbon


def verify(base: str, root: Path) -> dict:
    workspace = root / "Demo Python Repository"
    write_fixture(workspace, "src/demo1/__init__.py", '"""Demo1 Python Package."""\n__version__ = "0.1.0"\n')
    write_fixture(workspace, "src/demo1/cli.py", "def main():\n    return 'Run the authentication demonstration'\n")
    write_fixture(workspace, "src/demo1/services/auth.py",
                  "LOCKOUT_THRESHOLD = 3\n\ndef is_locked(failed_attempts):\n"
                  "    return failed_attempts >= LOCKOUT_THRESHOLD\n\n"
                  + "# Authentication audit documentation.\n" * 70)
    write_fixture(workspace, "src/demo1/models/user.py", "class User:\n    failed_attempts = 0\n")
    write_fixture(workspace, "tests/test_auth.py",
                  "from demo1.services.auth import is_locked\n\ndef test_lockout():\n"
                  "    assert is_locked(3)\n    assert not is_locked(2)\n")
    write_fixture(workspace, "README.md", "# Demo1\nCURRENT_PURPOSE: an authentication CLI and its lockout tests.\n")
    write_fixture(workspace, "pyproject.toml", '[project]\nname = "demo1"\n[project.scripts]\ndemo1 = "demo1.cli:main"\n')
    watch = {"workspace_root": str(workspace), "watcher_id": "context-results-smoke", "sequence": 1}
    assert request(base, "/index-workspace", {**watch, "action": "start"})["indexed_files"] == 5
    query = {"workspace_root": str(workspace), "query": "GIVE ME THE FULL OVERVIEW OF MY PROJECT",
             "token_budget": 4096, "max_candidates": 6}
    began = time.perf_counter()
    overview = request(base, "/prune-workspace", query)
    overview_ms = round((time.perf_counter() - began) * 1000, 2)
    assert overview["context_mode"] == "repository_overview"
    assert overview["structured_goal"]["task_type"] == "repository_overview"
    assert overview["structured_goal"]["identifiers"] == []
    names = {item["file_path"] for item in overview["files"]}
    assert names == {"README.md", "pyproject.toml", "src/demo1/cli.py",
                     "src/demo1/services/auth.py", "src/demo1/models/user.py", "tests/test_auth.py"}
    assert 0 < overview["pruned_tokens"] <= 4096
    assert overview["raw_context_tokens"] >= overview["pruned_tokens"]
    assert overview["original_tokens"] >= overview["retained_source_tokens"] > 0
    assert overview["index_cache_hit"] and overview["retrieval_cache_hit"]
    assert request(base, "/prune-workspace", query)["context_cache_hit"]
    carbon = carbon_comparison(base, overview)
    write_fixture(workspace, "README.md", "# Demo1\nUPDATED_PURPOSE: current project documentation.\n")
    updated = request(base, "/prune-workspace", query)
    assert not updated["context_cache_hit"] and "UPDATED_PURPOSE" in updated["unified_prompt"]
    write_fixture(workspace, ".agents/tokenwise.json", json.dumps({
        "backend_port": urlparse(base).port, "auto_start_backend": False,
        "token_budget": 4096, "max_candidates": 6,
    }))
    runtime = root / "Adapter Runtime"
    write_fixture(runtime, "backend.json", json.dumps({"port": urlparse(base).port, "project_root": str(ROOT)}))
    adapter = subprocess.run(
        [sys.executable, "-m", "swe_pruner.antigravity_context", "--workspace", str(workspace),
         "--query-stdin", "--verification"], input=query["query"], capture_output=True,
        text=True, encoding="utf-8", timeout=40, check=True,
        env={**os.environ, "PYTHONPATH": str(SOURCE / "src"), "PYTHONUTF8": "1",
             "TOKENWISE_RUNTIME_DIR": str(runtime)},
    )
    activity = json.loads((workspace / ".tokenwise/latest.json").read_text(encoding="utf-8"))
    assert activity["status"] == "ready" and activity["backend_url"] == base
    assert activity["result"]["context_mode"] == "repository_overview"
    assert activity["result"]["raw_context_tokens"] == updated["raw_context_tokens"]
    assert adapter.stdout.replace("\r\n", "\n") == updated["unified_prompt"]
    focused_query = {**query, "query": "Explain LOCKOUT_THRESHOLD account lockout and its related tests"}
    began = time.perf_counter()
    focused = request(base, "/prune-workspace", focused_query)
    focused_ms = round((time.perf_counter() - began) * 1000, 2)
    assert focused["context_mode"] == "focused"
    assert "src/demo1/services/auth.py" in {item["file_path"] for item in focused["files"]}
    assert "tests/test_auth.py" in {item["file_path"] for item in focused["files"]}
    assert 0 < focused["pruned_tokens"] <= 4096
    focused_carbon = carbon_comparison(base, focused)
    scaffold = root / "Scaffold Only"
    write_fixture(scaffold, "src/demo1/__init__.py", '"""Demo1 Python Package."""\n__version__ = "0.1.0"\n')
    sparse = request(base, "/prune-workspace", {**query, "workspace_root": str(scaffold)})
    assert sparse["retained_source_tokens"] == sparse["original_tokens"]
    assert sparse["raw_context_tokens"] == sparse["pruned_tokens"]
    assert sparse["context_overhead_tokens"] > 0
    assert any("Only Python package initializers" in warning for warning in sparse["warnings"])
    sparse_carbon = carbon_comparison(base, sparse)
    assert sparse_carbon["carbonSavings"]["co2GramsSaved"] == 0
    request(base, "/index-workspace", {**watch, "action": "stop", "sequence": 2})
    return {"checks": {"real_model_loaded": True, "overview_files": len(names),
                       "overview_ms": overview_ms, "focused_neural_ms": focused_ms,
                       "documentation_cache_invalidation": True, "carbon_mapping": True,
                       "antigravity_adapter_metrics": True,
                       "scaffold_zero_source_reduction": True, "antigravity_cloud_called": False},
            "overview": {**overview, **carbon}, "focused": {**focused, **focused_carbon},
            "scaffold": {**sparse, **sparse_carbon}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Optional JSON results for panel verification.")
    args = parser.parse_args()
    if not (SOURCE / "model/model.safetensors").is_file():
        parser.error("Install the pinned local weights first; this verifier never downloads them.")
    if not (ROOT / "vscode-extension/dist/services/carbonComparison.js").is_file():
        parser.error("Run npm run compile in vscode-extension first.")
    scratch = ROOT / "tmp"
    scratch.mkdir(exist_ok=True)
    with isolated_directory(scratch) as root:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1",
                       "PYTHONPATH": str(SOURCE / "src"), "SWEPRUNER_MODEL_PATH": str(SOURCE / "model"),
                       "SWEPRUNER_CARBON_ARTIFACTS_DIR": str(SOURCE / "carbon_artifacts"),
                       "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        log = root / "backend.log"
        with log.open("w", encoding="utf-8") as output:
            process = subprocess.Popen([sys.executable, "-m", "uvicorn", "swe_pruner.online_serving:app",
                                        "--host", "127.0.0.1", "--port", str(port)],
                                       cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            try:
                print("Starting an isolated backend with real local weights and carbon artifacts.", flush=True)
                deadline = time.monotonic() + 90
                health = {}
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        health = request(base, "/health")
                        if health.get("model_loaded"):
                            break
                    except (URLError, TimeoutError):
                        pass
                    time.sleep(.3)
                assert health.get("model_loaded") and health.get("carbon_models_loaded"), health
                result = verify(base, root)
                print(json.dumps(result["checks"], indent=2), flush=True)
                if args.report:
                    args.report.parent.mkdir(parents=True, exist_ok=True)
                    args.report.write_text(json.dumps(result, indent=2), encoding="utf-8")
            except Exception:
                print(log.read_text(encoding="utf-8")[-6000:], file=sys.stderr)
                raise
            finally:
                if process.poll() is None:
                    if os.name == "nt":
                        # Python's private-environment launcher may own a child interpreter.
                        subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                    else:
                        process.terminate()
                process.wait(timeout=20)
                if os.name == "nt":
                    time.sleep(1)
    print("Owned backend stopped; isolated sample repositories removed.", flush=True)


if __name__ == "__main__":
    main()
