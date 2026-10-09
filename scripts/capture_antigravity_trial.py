"""Capture one fresh native baseline trial; never manufacture missing telemetry."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "demonstration" / "comparative_study"


def fingerprint(folder):
    digest = hashlib.sha256()
    for file in sorted(folder.rglob("*"), key=lambda p: p.relative_to(folder).as_posix()):
        if file.is_file():
            digest.update(file.relative_to(folder).as_posix().encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()


def summarize_trace(text, expected_model):
    """Keep failed-run usage, but never promote an empty SUCCESS to an answer."""
    events = [json.loads(line) for line in text.splitlines() if line.strip()]
    results = [event.get("result") for event in events if event.get("event") == "result"]
    if len(results) != 1 or not isinstance(results[0], dict):
        return {"status": "invalid_trace", "reason": "Expected exactly one terminal result"}
    result = results[0]
    conversation = result.get("conversation_id")
    if not isinstance(conversation, str) or not conversation.strip() or result.get("num_turns") != 1:
        return {"status": "invalid_trace", "reason": "Expected a fresh single-turn conversation"}
    inits = [event for event in events if event.get("event") == "init"]
    if len(inits) != 1 or inits[0].get("init", {}).get("model") != expected_model:
        return {"status": "invalid_trace", "reason": "Pinned model not confirmed"}
    steps = {}
    for event in events:
        step = event.get("step_update", {})
        if event.get("event") == "init" and event.get("conversation_id") != conversation:
            return {"status": "invalid_trace", "reason": "Mixed conversations"}
        if step and step.get("conversation_id") != conversation:
            return {"status": "invalid_trace", "reason": "Mixed conversations"}
        if step.get("step_type") == "tool" and step.get("state") in ("DONE", "ERROR"):
            index = step.get("step_index")
            if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                return {"status": "invalid_trace", "reason": "Invalid tool index"}
            steps[index] = step
    usage = result.get("usage", {})
    counters = {}
    for key in ("input_tokens", "output_tokens", "total_tokens", "thinking_tokens", "cache_read_tokens"):
        value = usage.get(key) if isinstance(usage, dict) else None
        counters[key] = value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None
    answer = result.get("response")
    answer_present = isinstance(answer, str) and bool(answer.strip())
    status = "captured_ungraded"
    if result.get("denied_actions"):
        status = "permission_denied"
    elif result.get("status") != "SUCCESS":
        status = "agent_failed"
    elif not answer_present:
        status = "empty_answer"
    elif not counters["total_tokens"]:
        status = "usage_unavailable"
    return {"status": status, "conversation_id": conversation, "model": expected_model,
            "answer_present": answer_present, "reported_usage": counters,
            "reported_duration_seconds": result.get("duration_seconds"),
            "observed_attempted_tool_calls": len(steps),
            "observed_completed_tool_calls": sum(s.get("state") == "DONE" for s in steps.values()),
            "observed_failed_tool_calls": sum(s.get("state") == "ERROR" for s in steps.values()),
            "tool_trace": [steps[key] for key in sorted(steps)],
            "denied_actions": result.get("denied_actions", []),
            "answer": answer if answer_present else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="01_click")
    parser.add_argument("--pair", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--model", required=True)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--cli", type=Path, default=ROOT / "tmp" / "agy.exe")
    args = parser.parse_args()
    entries = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))["repositories"]
    entry = next((e for e in entries if e["folder"] == args.repository), None)
    if not entry:
        parser.error("Unknown repository")
    folder = CORPUS / args.repository
    if any((folder / name).exists() for name in (".agents", ".tokenwise", "AGENTS.md", "GEMINI.md")):
        parser.error("Baseline has potential instruction/context contamination; inspect before running")
    rubric = CORPUS / "rubrics" / f"{args.repository}.json"
    if not rubric.is_file():
        parser.error("Freeze a six-fact source-grounded rubric first")
    source_before = fingerprint(folder)
    if source_before != entry["regular_file_fingerprint"]:
        parser.error("Source differs from the pinned snapshot; restore only through reviewed preparation")
    destination = CORPUS / "results" / f"{args.repository}-pair{args.pair}-without"
    destination.mkdir(parents=True, exist_ok=False)
    prompt = entry["task"] + "\nCite relevant files, functions and test names. If evidence is missing, say so instead of guessing."
    command = [str(args.cli.resolve()), "-p", prompt, "--model", args.model,
               "--output-format", "stream-json", "--print-timeout", f"{args.timeout}s"]
    metadata = {"condition": "without", "repository": entry, "pair": args.pair,
                "measurement_scope": "native_antigravity_cli", "model": args.model,
                "prompt": prompt, "command": command, "started_utc": datetime.now(timezone.utc).isoformat(),
                "rubric_sha256": hashlib.sha256(rubric.read_bytes()).hexdigest(),
                "source_before": source_before, "correct_supported_facts": None,
                "incorrect_or_unsupported_claims": None}
    started = time.perf_counter()
    try:
        with (destination / "stdout.jsonl").open("wb") as stdout, (destination / "stderr.txt").open("wb") as stderr:
            process = subprocess.Popen(command, cwd=folder, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL)
            try:
                metadata["exit_code"] = process.wait(timeout=args.timeout + 30)
                metadata["status"] = "captured_unvalidated" if process.returncode == 0 else "cli_failed"
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                metadata.update(status="timeout", exit_code=process.returncode)
    except OSError as error:
        metadata.update(status="launch_failed", error=str(error))
    finally:
        metadata["total_answer_time_seconds"] = round(time.perf_counter() - started, 3)
        metadata["source_after"] = fingerprint(folder)
        metadata["source_unchanged"] = metadata["source_before"] == metadata["source_after"]
        if metadata["status"] == "captured_unvalidated":
            try:
                metadata.update(summarize_trace((destination / "stdout.jsonl").read_text(encoding="utf-8"), args.model))
            except (ValueError, TypeError, AttributeError) as error:
                metadata.update(status="invalid_trace", error=str(error))
        if not metadata["source_unchanged"]:
            metadata["status"] = "source_modified"
        (destination / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result_directory": str(destination), "status": metadata["status"],
                      "seconds": metadata["total_answer_time_seconds"], "source_unchanged": metadata["source_unchanged"]}))


if __name__ == "__main__":
    main()
