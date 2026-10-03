"""Portable bootstrap; the actual adapter runs in TokenWise's private environment."""
import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook", action="store_true")
    parser.add_argument("--query-stdin", action="store_true")
    parser.add_argument("--query-base64")
    parser.add_argument("--verification", action="store_true")
    args = parser.parse_args()
    try:
        workspace = Path(__file__).resolve().parents[2]
        link = json.loads((workspace / ".tokenwise/backend-link.json").read_text(encoding="utf-8-sig"))
        if link.get("schema_version") != 1 or not Path(link["registration_path"]).is_absolute():
            raise ValueError("Invalid backend link. Run TokenWise: Enable Automatic Context again.")
        registration = json.loads(Path(link["registration_path"]).read_text(encoding="utf-8-sig"))
        root = Path(registration["project_root"])
        runtime = Path(registration["runtime_dir"])
        python = root / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
        if (registration.get("schema_version") != 1 or not root.is_absolute() or not runtime.is_absolute()
                or Path(registration["python_path"]) != python or not python.is_file()):
            raise ValueError("The backend has moved or is incomplete. Run TokenWise setup again.")
        os.environ.update({"TOKENWISE_RUNTIME_DIR": str(runtime), "PYTHONUTF8": "1"})
        script = root / "scripts" / ("antigravity_hook.py" if args.hook else "antigravity_context.py")
        command = [str(python), str(script), "--workspace", str(workspace)]
        if not args.hook:
            if args.query_stdin:
                command.append("--query-stdin")
            elif args.query_base64 is not None:
                command += ["--query", base64.b64decode(args.query_base64, validate=True).decode("utf-8")]
            else:
                raise ValueError("Provide --query-stdin or --query-base64 for a context request.")
            if args.verification:
                command.append("--verification")
        status = subprocess.call(command)
        if status and args.hook:
            print("{}")
            return 0
        return status
    except Exception as exc:
        print("TokenWise: " + str(exc), file=sys.stderr)
        if args.hook:
            print("{}")
            return 0
        return 1


if __name__ == "__main__":
    sys.exit(main())
