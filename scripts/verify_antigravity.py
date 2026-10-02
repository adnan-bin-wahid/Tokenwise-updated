"""Verify real retrieval and both Windows adapters, without calling Antigravity's cloud model."""

import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "swe-pruner/swe-pruner/src"))

from swe_pruner.antigravity_hook import DEFAULTS, MARKER, ensure_backend, request_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=PROJECT_ROOT / "Test_project")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    base_url = ensure_backend(PROJECT_ROOT, DEFAULTS)
    query = "Explain the payment retry logic and its related tests."
    started = time.monotonic()
    result = request_json(f"{base_url}/prune-workspace", {
        "query": query, "workspace_root": str(workspace), "token_budget": 4096, "max_candidates": 6,
    }, timeout=180)
    paths = {item["file_path"] for item in result["files"]}
    assert "services/payment_service.py" in paths, paths
    assert "tests/test_payment.py" in paths, paths
    assert result["pruned_tokens"] <= 4096, result["pruned_tokens"]
    assert result["unified_prompt"].startswith(MARKER)
    assert "MAX_PAYMENT_RETRIES = 3" in result["unified_prompt"], "Retry configuration must remain available"
    print(f"Automatic discovery: {len(paths)} files, {result['pruned_tokens']} tokens, {time.monotonic() - started:.2f}s", flush=True)

    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(PROJECT_ROOT / "swe-pruner/swe-pruner/model/tokenizer.json"))
    assert len(tokenizer.encode(result["unified_prompt"], add_special_tokens=False).ids) == result["pruned_tokens"]

    runtime = workspace / ".tokenwise/verification"
    runtime.mkdir(parents=True, exist_ok=True)
    transcript = runtime / "transcript.jsonl"
    transcript.write_text(json.dumps({
        "type": "USER_INPUT", "source": "USER_EXPLICIT", "step_index": 1, "content": query,
    }) + "\n", encoding="utf-8")
    payload = {
        "conversationId": "tokenwise-verification-" + uuid.uuid4().hex,
        "workspacePaths": [str(workspace)], "transcriptPath": str(transcript),
        "invocationNum": 0, "initialNumSteps": 1,
        "tokenwiseVerification": True,
    }
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".agents/tokenwise-hook.ps1"]

    def invoke(invocation: int) -> dict:
        execution = subprocess.run(
            command, input=json.dumps({**payload, "invocationNum": invocation}),
            text=True, encoding="utf-8", capture_output=True, cwd=workspace, timeout=150,
        )
        assert execution.returncode == 0, execution.stderr
        output = json.loads(execution.stdout)
        assert not execution.stderr, execution.stderr
        return output

    injected = invoke(0)
    assert injected["injectSteps"][0]["userMessage"].startswith(MARKER), injected
    assert len(tokenizer.encode(injected["injectSteps"][0]["userMessage"], add_special_tokens=False).ids) <= 4096
    assert invoke(1) == {}, "The same user turn must not be injected twice"
    print("PowerShell hook: valid injection JSON; subsequent invocation skipped", flush=True)

    tiny = request_json(f"{base_url}/prune-workspace", {
        "query": query, "workspace_root": str(workspace), "token_budget": 256, "max_candidates": 3,
    }, timeout=180)
    assert tiny["files"], tiny
    assert len(tokenizer.encode(tiny["unified_prompt"], add_special_tokens=False).ids) <= 256
    print(f"Strict small-budget check: {tiny['pruned_tokens']}/256 tokens", flush=True)

    auth_query = "Explain user's account lockout after failed login attempts, including \"AuthService\" and its related tests. \u2713"
    escaped_query = auth_query.replace("'", "''")
    agent_command = (
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise-context.ps1 "
        f"-QueryBase64 ([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('{escaped_query}'))) -Verification"
    )
    execution = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", agent_command],
        text=True, encoding="utf-8", capture_output=True, cwd=workspace, timeout=150,
    )
    assert execution.returncode == 0, execution.stderr
    assert not execution.stderr, execution.stderr
    assert execution.stdout.startswith(MARKER), execution.stdout[:200]
    activity = json.loads((workspace / ".tokenwise/latest.json").read_text(encoding="utf-8"))
    assert activity["query"] == auth_query, activity["query"]
    assert activity["transport"] == "antigravity-agent-command"
    assert activity["verification"] is True
    paths = {item["file_path"] for item in activity["result"]["files"]}
    assert "services/auth_service.py" in paths, paths
    assert "tests/test_auth.py" in paths, paths
    # PowerShell appends line endings; they are transport framing, not part of the packed context.
    assert execution.stdout.rstrip("\r\n").replace("\r\n", "\n") == activity["result"]["unified_prompt"].rstrip("\r\n")
    assert len(tokenizer.encode(activity["result"]["unified_prompt"], add_special_tokens=False).ids) <= 4096
    print(f"Agent-command fallback: auth service + tests, {activity['result']['pruned_tokens']} tokens; quotes preserved", flush=True)
    print("ANTIGRAVITY_INTEGRATION_OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
