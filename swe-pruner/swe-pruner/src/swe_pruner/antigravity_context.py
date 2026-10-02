"""Return bounded context through the agent's command tool when native hooks are unavailable."""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .antigravity_hook import load_settings, retrieve_context, write_json


def run_context(query: str, project_root: Path, workspace: Path, verification: bool = False) -> str | None:
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
        base_url, result = retrieve_context(project_root, workspace, event["query"], settings)
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
    args = parser.parse_args()
    root = project_root or Path(__file__).resolve().parents[4]
    query = sys.stdin.read() if args.query_stdin else args.query
    context = run_context(query, root, args.workspace.resolve(), args.verification)
    if context is None:
        return 1
    # Nothing except the bounded repository context goes to the agent's tool output.
    print(context, end="", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
