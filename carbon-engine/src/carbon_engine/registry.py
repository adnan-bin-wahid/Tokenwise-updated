from __future__ import annotations

import pandas as pd


def build_model_registry(merged_df: pd.DataFrame) -> dict[str, dict[str, float | str]]:
    required = [
        "model_name",
        "model_size_b",
        "mmlu_pro_score",
        "bbh_score",
        "latency_per_input_token_ms",
        "latency_per_output_token_ms",
        "gpu_type",
    ]
    missing = [col for col in required if col not in merged_df.columns]
    if missing:
        raise ValueError(f"Merged dataset missing required columns for registry: {missing}")

    grouped = merged_df.groupby("model_name", dropna=True)
    registry: dict[str, dict[str, float | str]] = {}

    for model_name, frame in grouped:
        key = str(model_name).strip().lower()
        if not key:
            continue

        gpu_mode = (
            frame["gpu_type"].astype(str).str.strip().str.lower().mode().iloc[0]
            if not frame["gpu_type"].empty
            else "nvidia-a100-80gb"
        )

        registry[key] = {
            "model_size_b": float(pd.to_numeric(frame["model_size_b"], errors="coerce").median()),
            "mmlu_pro_score": float(pd.to_numeric(frame["mmlu_pro_score"], errors="coerce").median()),
            "bbh_score": float(pd.to_numeric(frame["bbh_score"], errors="coerce").median()),
            "latency_per_input_token_ms": float(
                pd.to_numeric(frame["latency_per_input_token_ms"], errors="coerce").median()
            ),
            "latency_per_output_token_ms": float(
                pd.to_numeric(frame["latency_per_output_token_ms"], errors="coerce").median()
            ),
            "gpu_type": gpu_mode,
        }

    return registry
