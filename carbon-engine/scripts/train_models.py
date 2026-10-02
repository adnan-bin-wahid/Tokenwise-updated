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

from carbon_engine.io_utils import load_table
from carbon_engine.modeling import save_models, train_all_models


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train SEAL phase-specific interpolation and extrapolation models.")
    parser.add_argument("--features-input", required=True, help="Engineered features parquet/csv path")
    parser.add_argument("--artifacts-dir", required=True, help="Directory where trained model artifacts are saved")
    parser.add_argument("--metrics-output", required=True, help="JSON output for CV metrics")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    feature_df = load_table(args.features_input)

    models, metrics = train_all_models(feature_df)
    save_models(models, args.artifacts_dir)

    metrics_payload = {name: asdict(metric) for name, metric in metrics.items()}
    metrics_path = Path(args.metrics_output)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    print(json.dumps(metrics_payload, indent=2))
    print(f"Saved model artifacts to: {args.artifacts_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
