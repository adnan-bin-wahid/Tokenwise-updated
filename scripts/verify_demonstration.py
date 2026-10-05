"""Real-weight checks on the single demonstration in an owned backend process."""

import importlib.util
import ast
import argparse
import json
import os
import socket
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from unittest.mock import patch

from verify_context_results import ROOT, SOURCE, isolated_directory, request


def verify_pruning_inputs(base, storage, demo):
    case = demo.cases()[0]
    directory = demo.ROOT / case["project"]
    filename = directory / case["mixed_selection_file"]
    source = filename.read_text(encoding="utf-8")
    query = case["session_query"]
    repository = request(base, "/prune-workspace", {"workspace_root": str(directory), "query": query,
                         "token_budget": 4096, "max_candidates": 8})
    assert repository["input_trace"]["mode"] == "repository"
    assert repository["structured_goal"]["excluded_topics"] == ["invoice pricing"]
    assert "invoice" not in repository["structured_goal"]["identifiers"]
    assert "def invoice_total" not in repository["unified_prompt"]
    assert "def test_invoice_total" not in repository["unified_prompt"]
    assert "invoice_total(" not in repository["unified_prompt"]
    for name in ("session_is_valid", "revoke_session", "test_session_expiry_boundary", "test_revocation"):
        assert name in repository["unified_prompt"], name
    carbon = subprocess.run(["node", str(ROOT / "scripts/verify-carbon-client.cjs")], cwd=ROOT,
        input=json.dumps({"base": base, "before": repository["raw_context_tokens"],
                          "after": repository["pruned_tokens"], "zero_overrides": True}),
        capture_output=True, text=True, encoding="utf-8", timeout=30, check=True)
    repository.update(json.loads(carbon.stdout))
    assert repository["carbonStatus"] == "ready"
    assert "request_overrides" not in repository["carbonAfter"]["featuresSource"]

    def manual(code, mode, first_line, threshold=.45):
        result = subprocess.run(["node", str(ROOT / "scripts/verify-pruning-client.cjs")], cwd=ROOT,
            input=json.dumps({"base": base, "query": query, "code": code, "file_path": str(filename),
                              "threshold": threshold, "mode": mode, "first_line": first_line, "zero_overrides": True}),
            capture_output=True, text=True, encoding="utf-8", timeout=120, check=True)
        mapped = json.loads(result.stdout)
        assert mapped["originalCode"] == code and mapped["lineScores"]
        assert mapped["input_trace"]["mode"] == mode
        assert mapped["carbonStatus"] == "ready"
        return mapped

    entire = manual(source, "selected_file", 1)
    stricter = manual(source, "selected_file", 1, .85)
    assert stricter["input_trace"]["threshold"] == .85
    assert stricter["originTokenCount"] == entire["originTokenCount"]
    assert stricter["lineScores"].keys() == entire["lineScores"].keys()
    assert all(abs(score - stricter["lineScores"][line]) < .0001 for line, score in entire["lineScores"].items())
    assert set(stricter["keptFrags"]).issubset(entire["keptFrags"])
    function = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "session_is_valid")
    excerpt = manual(ast.get_source_segment(source, function), "selected_excerpt", function.lineno)
    assert "invoice_total" not in excerpt["originalCode"]
    sys.path.insert(0, str(SOURCE / "src"))
    from swe_pruner.antigravity_hook import run_hook
    workspace = storage / "conversation-workspace"
    shutil.copytree(directory, workspace,
                    ignore=shutil.ignore_patterns("__pycache__", ".agents", ".tokenwise"))
    transcript = workspace / "transcript.jsonl"
    payload = {"workspacePaths": [str(workspace)], "transcriptPath": str(transcript),
               "conversationId": "tokenwise-verification-pruning-history", "tokenwiseVerification": True}
    with patch("swe_pruner.antigravity_hook.ensure_backend", return_value=base):
        for number, task in enumerate(("Explain account lockout after failed login attempts.",
                                       "What about its expiry boundary?", "Which tests cover that behavior?")):
            with transcript.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"type": "USER_INPUT", "source": "USER_EXPLICIT", "step_index": number, "content": task}) + "\n")
            assert run_hook(payload, ROOT, workspace).get("injectSteps")
        conversation = json.loads((workspace / ".tokenwise/latest.json").read_text(encoding="utf-8"))["result"]
        trace = conversation["input_trace"]
        assert trace["history_source"] == "native_scoped_user_turns"
        assert "account lockout" in trace["history_text"] and "expiry boundary" in trace["history_text"]
        assert trace["history_text"] in trace["effective_query"]
        assert run_hook({**payload, "conversationId": "tokenwise-verification-new-chat"}, ROOT, workspace).get("injectSteps")
        new_chat = json.loads((workspace / ".tokenwise/latest.json").read_text(encoding="utf-8"))["result"]
        assert not new_chat["context_hint_used"] and new_chat["structured_goal"]["clarification_required"]
    report = {"repository": repository, "selected_file": entire, "selected_high_threshold": stricter, "selected_excerpt": excerpt,
              "conversation": conversation, "new_chat": new_chat,
              "verification_only": True, "antigravity_cloud_called": False}
    (demo.ROOT / "results/pruning-inputs.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Real pruning inputs verified: repository, whole file/two thresholds, excerpt, native user history, new-chat isolation.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs-only", action="store_true", help="Retry just the real pruning-input paths, without regenerating packet comparisons.")
    parser.add_argument("--startup-timeout", type=int, default=180,
                        help="Seconds allowed for local model startup (30-600, default: 180).")
    arguments = parser.parse_args()
    if not 30 <= arguments.startup_timeout <= 600:
        parser.error("--startup-timeout must be between 30 and 600 seconds")
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
                deadline = time.monotonic() + arguments.startup_timeout
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
                (ROOT / "demonstration/results").mkdir(exist_ok=True)
                rows = [] if arguments.inputs_only else demo.compare_projects(base, ROOT / "demonstration/results")
                verify_pruning_inputs(base, storage, demo)
                if arguments.inputs_only:
                    return
                case = demo.cases()[0]
                payload = {"workspace_root": str(demo.ROOT / case["project"]), "token_budget": 4096, "max_candidates": 8}
                follow = request(base, "/prune-workspace", {**payload, "query": case["follow_up"], "context_hint": case["query"]})
                assert follow["context_hint_used"]
                assert "tests/test_auth.py" in [file["file_path"] for file in follow["files"]]
                new_chat = request(base, "/prune-workspace", {**payload, "query": case["follow_up"]})
                assert not new_chat["context_hint_used"] and new_chat["structured_goal"]["clarification_required"]
                switched = request(base, "/prune-workspace", {**payload, "query": case["topic_switch"], "context_hint": case["query"]})
                assert not switched["context_hint_used"]
                assert "workflows.py" in [file["file_path"] for file in switched["files"]]
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
