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

from carbon_engine.inference import DualModeRegressorEngine, EstimationRequest


# Reference points from the paper's external comparison setup.
WILKINS_REFERENCE = [
    {
        "name": "llama2_7b",
        "empirical_joules": 349.96,
        "request": EstimationRequest(
            n_input_tokens=38,
            n_output_tokens=64,
            model_size_b=7.0,
            latency_per_input_token_ms=0.9,
            latency_per_output_token_ms=2.0,
            gpu_encoded=0,
            mmlu_pro_score=0.32,
            bbh_score=0.38,
        ),
    },
    {
        "name": "llama2_13b",
        "empirical_joules": 602.27,
        "request": EstimationRequest(
            n_input_tokens=38,
            n_output_tokens=64,
            model_size_b=13.0,
            latency_per_input_token_ms=1.1,
            latency_per_output_token_ms=2.4,
            gpu_encoded=0,
            mmlu_pro_score=0.36,
            bbh_score=0.41,
        ),
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run external SEAL validation checkpoints.")
    parser.add_argument("--artifacts-dir", required=True, help="Directory with trained model artifacts")
    parser.add_argument("--output", required=True, help="JSON output report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    engine = DualModeRegressorEngine(args.artifacts_dir)

    report = []
    errors = []

    for row in WILKINS_REFERENCE:
        prediction = engine.predict(row["request"])
        relative_error_pct = abs(prediction.total_joules - row["empirical_joules"]) / row["empirical_joules"] * 100.0
        report.append(
            {
                "name": row["name"],
                "empirical_joules": row["empirical_joules"],
                "predicted_joules": prediction.total_joules,
                "relative_error_pct": relative_error_pct,
                "prefill_route": prediction.prefill_route,
                "decode_route": prediction.decode_route,
            }
        )
        errors.append(relative_error_pct)

    summary = {
        "samples": report,
        "average_relative_error_pct": sum(errors) / len(errors) if errors else 0.0,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
