from __future__ import annotations

from dataclasses import dataclass

LLM_PERF_REQUIRED_COLUMNS = [
    "model_name",
    "precision",
    "num_input_tokens",
    "num_output_tokens",
    "latency_per_input_token_ms",
    "latency_per_output_token_ms",
    "prefill_energy_j",
    "decode_energy_j",
    "gpu_type",
]

OPEN_LLM_REQUIRED_COLUMNS = [
    "model_name",
    "precision",
    "model_size_b",
    "mmlu_pro_score",
    "bbh_score",
]

MERGED_REQUIRED_COLUMNS = [
    *LLM_PERF_REQUIRED_COLUMNS,
    "model_size_b",
    "mmlu_pro_score",
    "bbh_score",
]


@dataclass(frozen=True)
class MergeStats:
    llm_perf_rows: int
    open_llm_rows: int
    merged_rows: int
    deduped_rows: int
    dropped_missing_rows: int


def canonicalize_model_name(value: str) -> str:
    parts = value.strip().lower().split("/")
    name = parts[-1]
    return " ".join(name.split())


def canonicalize_precision(value: str) -> str:
    return value.strip().lower().replace("fp", "float")


def canonicalize_gpu_type(value: str) -> str:
    val = value.strip()
    if val.startswith("[") and val.endswith("]"):
        val = val.strip("[]'\" ")
    
    val_lower = val.lower()
    if "a100" in val_lower:
        return "nvidia-a100-80gb"
    elif "a10" in val_lower:
        return "nvidia-a10g"
    elif "t4" in val_lower:
        return "nvidia-t4"
    elif "v100" in val_lower:
        return "nvidia-v100"
    elif "l4" in val_lower:
        return "nvidia-l4"
    elif "l40" in val_lower:
        return "nvidia-l40"
    elif "h100" in val_lower:
        return "nvidia-h100"
    elif "a30" in val_lower:
        return "nvidia-a30"
        
    return val_lower
