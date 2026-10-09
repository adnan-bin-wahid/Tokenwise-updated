"""Return bounded context through the agent's command tool when native hooks are unavailable."""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .antigravity_hook import load_settings, retrieve_context, write_json
from .conversation_context import MESSAGE_LIMIT, STORED_TURN_LIMIT


def run_context(query: str, project_root: Path, workspace: Path, verification: bool = False, history: list[str] | None = None) -> str | None:
    started = time.monotonic()
    activity_path = workspace / ".tokenwise/latest.json"
    event = {
        "event_id": uuid.uuid4().hex, "timestamp": datetime.now(timezone.utc).isoformat(),
        "transport": "antigravity-agent-command", "status": "retrieving",
        "verification": verification, "query": query.strip(),
    }
    try:
        if not workspace.is_dir():
            raise ValueError("The TokenWise workspace does not exist.")
        if not event["query"]:
            raise ValueError("A non-empty user request is required.")
        settings = load_settings(workspace)
        if not settings["enabled"]:
            raise RuntimeError("Automatic TokenWise context is disabled in .agents/tokenwise.json.")
        write_json(activity_path, event)
        if history is not None and (not isinstance(history, list) or len(history) > STORED_TURN_LIMIT
                                   or any(not isinstance(turn, str) or len(turn) > MESSAGE_LIMIT for turn in history)):
            raise ValueError("History must be at most 32 user strings of at most 2000 characters each.")
        base_url, result = retrieve_context(project_root, workspace, event["query"], settings, history=history)
        if isinstance(result.get("input_trace"), dict) and history and settings["conversation_memory"]:
            result["input_trace"]["history_source"] = "agent_supplied_user_turns"
        event.update({
            "status": "ready", "result": result, "backend_url": base_url,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        })
        write_json(activity_path, event)
        return result["unified_prompt"]
    except Exception as exc:
        event.update({"status": "error", "error": str(exc)})
        if workspace.is_dir():
            try:
                write_json(activity_path, event)
            except OSError:
                pass
        print(f"TokenWise: {exc}", file=sys.stderr)
        return None


def main(project_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    query_input = parser.add_mutually_exclusive_group(required=True)
    query_input.add_argument("--query")
    query_input.add_argument("--query-stdin", action="store_true")
    parser.add_argument("--verification", action="store_true")
    parser.add_argument("--history-base64", default="")
    args = parser.parse_args()
    root = project_root or Path(__file__).resolve().parents[4]
    query = sys.stdin.read() if args.query_stdin else args.query
    try:
        if len(args.history_base64) > 131072:
            raise ValueError("Encoded history is too large.")
        history = json.loads(base64.b64decode(args.history_base64, validate=True).decode("utf-8")) if args.history_base64 else None
    except (ValueError, UnicodeError) as exc:
        print(f"TokenWise: invalid user-history data: {exc}", file=sys.stderr)
        return 1
    context = run_context(query, root, args.workspace.resolve(), args.verification, history)
    if context is None:
        return 1
    # Nothing except the bounded repository context goes to the agent's tool output.
    print(context, end="", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
