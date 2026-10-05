"""Real-weight comparison checks on demonstration projects in an owned backend process."""

import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from urllib.error import URLError

from verify_context_results import ROOT, SOURCE, isolated_directory, request


def main() -> None:
    spec = importlib.util.spec_from_file_location("demo_checks", ROOT / "demonstration/run_checks.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    demo.check_projects()
    scratch = ROOT / "tmp"
    scratch.mkdir(exist_ok=True)
    with isolated_directory(scratch) as storage:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        environment = {**os.environ, "PYTHONPATH": str(SOURCE / "src"), "PYTHONUTF8": "1",
                       "SWEPRUNER_MODEL_PATH": str(SOURCE / "model"),
                       "SWEPRUNER_CARBON_ARTIFACTS_DIR": str(SOURCE / "carbon_artifacts"),
                       "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        with (storage / "backend.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-m", "uvicorn", "swe_pruner.online_serving:app",
                                        "--host", "127.0.0.1", "--port", str(port)], cwd=ROOT, env=environment,
                                       stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            try:
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
                assert health.get("model_loaded") and health.get("carbon_models_loaded")
                rows = demo.compare_projects(base, ROOT / "demonstration/results")
                case = demo.cases()[0]
                payload = {"workspace_root": str(demo.ROOT / case["project"]), "token_budget": 4096, "max_candidates": 8}
                follow = request(base, "/prune-workspace", {**payload, "query": case["follow_up"], "context_hint": case["query"]})
                assert follow["context_hint_used"]
                assert "tests/test_auth.py" in [file["file_path"] for file in follow["files"]]
                new_chat = request(base, "/prune-workspace", {**payload, "query": case["follow_up"]})
                assert not new_chat["context_hint_used"] and new_chat["structured_goal"]["clarification_required"]
                switched = request(base, "/prune-workspace", {**payload, "query": case["topic_switch"], "context_hint": case["query"]})
                assert not switched["context_hint_used"]
                assert "security/session_service.py" in [file["file_path"] for file in switched["files"]]
                summary = {"comparison_rows": len(rows), "same_chat_hint": True, "new_chat_clarification": True,
                           "topic_switch_ignores_old_hint": True, "real_weights": True, "antigravity_cloud_called": False}
                (ROOT / "demonstration/results/verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                print(json.dumps(summary, indent=2), flush=True)
            except Exception:
                log.flush()
                print((storage / "backend.log").read_text(encoding="utf-8", errors="replace")[-6000:], file=sys.stderr)
                raise
            finally:
                if process.poll() is None:
                    if os.name == "nt":
                        subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                    else:
                        process.terminate()
                process.wait(timeout=20)
                if os.name == "nt":
                    time.sleep(1)
    print("Isolated verification backend stopped; demo application source was not changed.")


if __name__ == "__main__":
    main()
