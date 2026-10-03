"""Small managed-backend health/start CLI, without importing the neural model."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "swe-pruner/swe-pruner/src"))
from swe_pruner.antigravity_hook import DEFAULTS, ensure_backend, request_json

parser = argparse.ArgumentParser()
parser.add_argument("--start", action="store_true")
args = parser.parse_args()
try:
    if args.start:
        base_url = ensure_backend(ROOT, {**DEFAULTS, "startup_timeout_seconds": 60})
        print(json.dumps({"backend_url": base_url, "health": request_json(base_url + "/health")}))
    else:
        base_url = ensure_backend(ROOT, {**DEFAULTS, "auto_start_backend": False})
        print(json.dumps({"backend_url": base_url, "health": request_json(base_url + "/health")}))
except Exception as exc:
    print(f"TokenWise: {exc}", file=sys.stderr)
    raise SystemExit(1)
