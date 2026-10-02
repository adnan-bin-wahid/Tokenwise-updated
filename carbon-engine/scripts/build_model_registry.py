from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_engine.io_utils import load_table
from carbon_engine.registry import build_model_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build model_registry.json from merged benchmark data")
    parser.add_argument("--merged-input", required=True, help="Merged benchmark dataset (csv/parquet)")
    parser.add_argument("--output", required=True, help="Output model_registry.json path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    merged_df = load_table(args.merged_input)
    registry = build_model_registry(merged_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    print(f"Wrote model registry with {len(registry)} entries to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
