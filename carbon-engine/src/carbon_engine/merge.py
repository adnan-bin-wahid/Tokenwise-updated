from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .schema import (
    LLM_PERF_REQUIRED_COLUMNS,
    MERGED_REQUIRED_COLUMNS,
    OPEN_LLM_REQUIRED_COLUMNS,
    MergeStats,
    canonicalize_model_name,
    canonicalize_precision,
    canonicalize_gpu_type,
)


def _validate_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {table_name}: {missing}")


def _normalize_join_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["model_name"] = out["model_name"].astype(str).map(canonicalize_model_name)
    out["precision"] = out["precision"].astype(str).map(canonicalize_precision)
    if "gpu_type" in out.columns:
        out["gpu_type"] = out["gpu_type"].astype(str).map(canonicalize_gpu_type)
    return out


def merge_benchmark_tables(llm_perf_df: pd.DataFrame, open_llm_df: pd.DataFrame) -> tuple[pd.DataFrame, MergeStats]:
    _validate_columns(llm_perf_df, LLM_PERF_REQUIRED_COLUMNS, "LLM-Perf")
    _validate_columns(open_llm_df, OPEN_LLM_REQUIRED_COLUMNS, "Open LLM")

    left = _normalize_join_keys(llm_perf_df)
    right = _normalize_join_keys(open_llm_df)

    merged = left.merge(
        right[
            [
                "model_name",
                "precision",
                "model_size_b",
                "mmlu_pro_score",
                "bbh_score",
            ]
        ],
        on=["model_name", "precision"],
        how="inner",
    )

    deduped = merged.drop_duplicates(subset=["model_name", "precision", "num_input_tokens", "num_output_tokens", "gpu_type"])
    before_drop_na = len(deduped)
    filtered = deduped.dropna(subset=MERGED_REQUIRED_COLUMNS)

    stats = MergeStats(
        llm_perf_rows=len(llm_perf_df),
        open_llm_rows=len(open_llm_df),
        merged_rows=len(merged),
        deduped_rows=len(deduped),
        dropped_missing_rows=before_drop_na - len(filtered),
    )

    return filtered, stats


def stats_to_dict(stats: MergeStats) -> dict[str, int]:
    return asdict(stats)
