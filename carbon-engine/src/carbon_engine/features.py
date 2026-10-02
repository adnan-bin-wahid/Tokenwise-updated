from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .schema import MERGED_REQUIRED_COLUMNS

FEATURE_COLUMNS = [
    "n_input_tokens",
    "n_output_tokens",
    "model_size_b",
    "latency_per_input_token_ms",
    "latency_per_output_token_ms",
    "gpu_encoded",
    "mmlu_pro_score",
    "bbh_score",
]

TARGET_COLUMNS = ["prefill_energy_j", "decode_energy_j"]


@dataclass(frozen=True)
class FeatureArtifacts:
    gpu_encoder: dict[str, int]
    interpolation_min_model_size_b: float
    interpolation_max_model_size_b: float



def _rename_for_training(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(
        columns={
            "num_input_tokens": "n_input_tokens",
            "num_output_tokens": "n_output_tokens",
            "gpu_type": "gpu_type",
        }
    )



def _fit_gpu_encoder(series: pd.Series) -> dict[str, int]:
    categories = sorted(series.astype(str).str.strip().str.lower().unique().tolist())
    return {name: idx for idx, name in enumerate(categories)}



def _encode_gpu(series: pd.Series, encoder: dict[str, int]) -> pd.Series:
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.map(encoder)



def prepare_training_features(
    merged_df: pd.DataFrame,
    interpolation_min_model_size_b: float = 7.0,
    interpolation_max_model_size_b: float = 111.0,
) -> tuple[pd.DataFrame, FeatureArtifacts]:
    missing = [col for col in MERGED_REQUIRED_COLUMNS if col not in merged_df.columns]
    if missing:
        raise ValueError(f"Merged dataset missing required columns: {missing}")

    working = _rename_for_training(merged_df).copy()

    encoder = _fit_gpu_encoder(working["gpu_type"])
    working["gpu_encoded"] = _encode_gpu(working["gpu_type"], encoder)

    ordered_columns = FEATURE_COLUMNS + TARGET_COLUMNS
    working = working[ordered_columns]
    working = working.dropna(subset=ordered_columns)

    numeric_columns = [
        "n_input_tokens",
        "n_output_tokens",
        "model_size_b",
        "latency_per_input_token_ms",
        "latency_per_output_token_ms",
        "gpu_encoded",
        "mmlu_pro_score",
        "bbh_score",
        "prefill_energy_j",
        "decode_energy_j",
    ]
    for col in numeric_columns:
        working[col] = pd.to_numeric(working[col], errors="coerce")

    working = working.dropna(subset=numeric_columns)

    working["is_interpolation"] = working["model_size_b"].between(
        interpolation_min_model_size_b,
        interpolation_max_model_size_b,
        inclusive="both",
    )

    artifacts = FeatureArtifacts(
        gpu_encoder=encoder,
        interpolation_min_model_size_b=interpolation_min_model_size_b,
        interpolation_max_model_size_b=interpolation_max_model_size_b,
    )

    return working, artifacts
