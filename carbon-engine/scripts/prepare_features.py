from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_engine.features import prepare_training_features
from carbon_engine.io_utils import load_table, save_parquet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create SEAL training features and artifacts.")
    parser.add_argument("--merged-input", required=True, help="Merged benchmark parquet/csv")
    parser.add_argument("--features-output", required=True, help="Output parquet for engineered features")
    parser.add_argument("--artifacts-output", required=True, help="Output JSON file for feature artifacts")
    parser.add_argument("--min-size", type=float, default=7.0, help="Interpolation min model size (B)")
    parser.add_argument("--max-size", type=float, default=111.0, help="Interpolation max model size (B)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    merged_df = load_table(args.merged_input)
    featured_df, artifacts = prepare_training_features(
        merged_df,
        interpolation_min_model_size_b=args.min_size,
        interpolation_max_model_size_b=args.max_size,
    )

    save_parquet(featured_df, args.features_output)

    artifacts_path = Path(args.artifacts_output)
    artifacts_path.parent.mkdir(parents=True, exist_ok=True)
    artifacts_path.write_text(json.dumps(asdict(artifacts), indent=2), encoding="utf-8")

    print(f"Saved engineered features to: {args.features_output}")
    print(f"Saved feature artifacts to: {args.artifacts_output}")
    print(f"Rows: {len(featured_df)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
