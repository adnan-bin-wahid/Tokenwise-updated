from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "swe-pruner/swe-pruner/src"))

from swe_pruner.antigravity_context import main


if __name__ == "__main__":
    raise SystemExit(main(PROJECT_ROOT))
