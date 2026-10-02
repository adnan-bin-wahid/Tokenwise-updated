from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
from huggingface_hub import hf_hub_download, list_repo_files


def _norm(s: str) -> str:
    return "".join(ch.lower() for ch in str(s) if ch.isalnum())


def _find_col(columns: Iterable[str], exact: list[str], contains: list[str]) -> str | None:
    cols = list(columns)
    norm_map = {_norm(c): c for c in cols}

    for candidate in exact:
        key = _norm(candidate)
        if key in norm_map:
            return norm_map[key]

    normalized_cols = [(_norm(c), c) for c in cols]
    for token in contains:
        nt = _norm(token)
        for nc, original in normalized_cols:
            if nt and nt in nc:
                return original

    return None


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _to_text(series: pd.Series, fallback: str = "") -> pd.Series:
    return series.astype(str).fillna(fallback)


def build_open_llm_table(data_dir: Path) -> tuple[pd.DataFrame, dict]:
    """Load Open LLM Leaderboard from local CSV or HF hub."""
    root = Path(__file__).resolve().parents[1]
    local_csv = root / "data" / "perf" / "llm-df.csv"
    
    if local_csv.exists():
        df = pd.read_csv(local_csv)
        print(f"[INFO] Loaded Open LLM Leaderboard from local {local_csv}")
    else:
        # Fallback: download from HF hub
        try:
            local_path = hf_hub_download(
                repo_id="open-llm-leaderboard/contents",
                filename="llm-df.csv",
                repo_type="dataset",
            )
            df = pd.read_csv(local_path)
        except Exception:
            raise RuntimeError("Could not load Open LLM Leaderboard from local or HF hub")

    model_col = _find_col(df.columns, ["model_name", "model", "Model"], ["model", "fullname"])
    precision_col = _find_col(df.columns, ["precision", "Precision"], ["precision", "dtype", "weighttype"])
    size_col = _find_col(df.columns, ["model_size_b", "params_b", "#Params (B)"], ["params", "modelsize", "sizeb"])
    mmlu_col = _find_col(df.columns, ["mmlu_pro_score", "MMLU-PRO Raw"], ["mmlupro", "mmlu"])
    bbh_col = _find_col(df.columns, ["bbh_score", "BBH Raw"], ["bbh"])

    missing = [
        name
        for name, value in {
            "model_name": model_col,
            "model_size_b": size_col,
            "mmlu_pro_score": mmlu_col,
            "bbh_score": bbh_col,
        }.items()
        if value is None
    ]
    if missing:
        raise RuntimeError(f"Open LLM dataset missing required semantic columns: {missing}")

    out = pd.DataFrame(
        {
            "model_name": _to_text(df[model_col]),
            "precision": _to_text(df[precision_col]) if precision_col else "unknown",
            "model_size_b": _to_numeric(df[size_col]),
            "mmlu_pro_score": _to_numeric(df[mmlu_col]),
            "bbh_score": _to_numeric(df[bbh_col]),
        }
    )

    out = out.dropna(subset=["model_name", "model_size_b", "mmlu_pro_score", "bbh_score"])
    out = out[out["model_name"].str.len() > 0]

    meta = {
        "rows_raw": int(len(df)),
        "rows_out": int(len(out)),
        "selected_columns": {
            "model_name": model_col,
            "precision": precision_col or "(filled=unknown)",
            "model_size_b": size_col,
            "mmlu_pro_score": mmlu_col,
            "bbh_score": bbh_col,
        },
    }

    out_path = data_dir / "open_llm_leaderboard.parquet"
    out.to_parquet(out_path, index=False)

    return out, meta


def _load_llm_perf_reports() -> tuple[pd.DataFrame, list[str]]:
    """Load LLM-Perf reports from local folder (preferred) or HF hub fallback."""
    root = Path(__file__).resolve().parents[1]
    local_perf_dir = root / "data" / "perf"
    
    frames: list[pd.DataFrame] = []
    used_files: list[str] = []
    
    # Try local folder first (search recursively for perf-df-*.csv files)
    if local_perf_dir.exists():
        import glob
        # Search in both perf/ and perf/data/ directories
        local_csvs = sorted(
            glob.glob(str(local_perf_dir / "perf-df-*.csv")) +
            glob.glob(str(local_perf_dir / "data" / "perf-df-*.csv"))
        )
        if local_csvs:
            for csv_path in local_csvs:
                df = pd.read_csv(csv_path)
                file_name = Path(csv_path).name
                df["source_file"] = file_name
                frames.append(df)
                used_files.append(file_name)
            print(f"[INFO] Loaded {len(local_csvs)} CSV files from local {local_perf_dir}")
            return pd.concat(frames, ignore_index=True), used_files
    
    # Fallback to HF hub download
    candidates = [
        ("optimum/llm-perf-dataset", "dataset", lambda f: f.endswith("perf-report.csv")),
        (
            "optimum-benchmark/llm-perf-leaderboard",
            "dataset",
            lambda f: f.endswith(".csv") and "perf-df" in f,
        ),
    ]

    selected_repo: tuple[str, str] | None = None
    perf_files: list[str] = []
    for repo_id, repo_type, file_filter in candidates:
        try:
            files = list_repo_files(repo_id, repo_type=repo_type)
            filtered = [f for f in files if file_filter(f)]
            if filtered:
                selected_repo = (repo_id, repo_type)
                perf_files = filtered
                break
        except Exception:
            continue

    if selected_repo is None:
        raise RuntimeError(
            "Could not access any public LLM-Perf source. Tried optimum/llm-perf-dataset and optimum-benchmark/llm-perf-leaderboard."
        )

    repo_id, repo_type = selected_repo

    for file_name in perf_files:
        local = hf_hub_download(
            repo_id=repo_id,
            filename=file_name,
            repo_type=repo_type,
        )
        df = pd.read_csv(local)
        df["source_file"] = file_name
        frames.append(df)
        used_files.append(file_name)

    if not frames:
        raise RuntimeError("No LLM-Perf benchmark CSV files found in selected source")

    return pd.concat(frames, ignore_index=True), used_files


def build_llm_perf_table(data_dir: Path) -> tuple[pd.DataFrame, dict]:
    raw, used_files = _load_llm_perf_reports()
    print(f"[DEBUG] Raw rows loaded: {len(raw)}, columns: {len(raw.columns)}")
    
    # Check if key columns exist
    print(f"[DEBUG] Has 'config.backend.model': {'config.backend.model' in raw.columns}")
    print(f"[DEBUG] Has 'report.prefill.latency.mean': {'report.prefill.latency.mean' in raw.columns}")
    print(f"[DEBUG] Has 'config.scenario.input_shapes.sequence_length': {'config.scenario.input_shapes.sequence_length' in raw.columns}")

    # Exact columns from optimum-benchmark/llm-perf-leaderboard schema.
    model_col = _find_col(raw.columns, ["config.backend.model", "model_name", "model"], ["backendmodel", "model"])
    precision_col = _find_col(raw.columns, ["config.backend.torch_dtype", "precision"], ["torchdtype", "precision", "weighttype"])
    in_tok_col = _find_col(raw.columns, ["config.scenario.input_shapes.sequence_length", "num_input_tokens"], ["sequencelength", "inputtokens", "inputlength"])
    out_tok_col = _find_col(raw.columns, ["config.scenario.new_tokens", "num_output_tokens"], ["newtokens", "outputtokens", "outputlength", "maxnewtokens"])
    lat_in_col = _find_col(raw.columns, ["report.prefill.latency.mean", "latency_per_input_token_ms"], ["prefilllatencymean", "latencyperinputtoken", "ttft"])
    lat_out_col = _find_col(raw.columns, ["report.decode.latency.mean", "latency_per_output_token_ms"], ["decodelatencymean", "latencyperoutputtoken", "tpot"])
    prefill_energy_col = _find_col(raw.columns, ["report.prefill.energy.total", "prefill_energy_j"], ["prefillenergytotal", "prefillenergy"])
    decode_energy_col = _find_col(raw.columns, ["report.decode.energy.total", "decode_energy_j"], ["decodeenergytotal", "decodeenergy"])
    gpu_col = _find_col(raw.columns, ["config.environment.gpu", "gpu_type", "gpu"], ["environmentgpu", "gpu", "hardware", "accelerator"])

    missing = [
        name
        for name, value in {
            "model_name": model_col,
            "num_input_tokens": in_tok_col,
            "latency_per_input_token_ms": lat_in_col,
            "latency_per_output_token_ms": lat_out_col,
            "gpu_type": gpu_col,
        }.items()
        if value is None
    ]
    if missing:
        raise RuntimeError(
            "LLM-Perf dataset missing required semantic columns. "
            f"Missing: {missing}. Available columns: {list(raw.columns)}"
        )

    # num_output_tokens is optional; use default or max_new_tokens if available
    if out_tok_col and out_tok_col in raw.columns:
        num_out_tok = _to_numeric(raw[out_tok_col])
        # If all NaN, fall back to default
        if num_out_tok.isna().all():
            num_out_tok = 128  # default estimate
    else:
        num_out_tok = 128  # default if column missing

    import numpy as np

    num_in = _to_numeric(raw[in_tok_col])
    num_out = _to_numeric(raw[out_tok_col]) if (out_tok_col and out_tok_col in raw.columns) else pd.Series([128.0]*len(raw), index=raw.index)
    num_out = num_out.fillna(128.0)

    raw_lat_in = _to_numeric(raw[lat_in_col])
    raw_lat_out = _to_numeric(raw[lat_out_col])

    # Convert total latency in seconds to ms per token:
    # (seconds * 1000) / num_tokens
    lat_in_ms_tok = (raw_lat_in * 1000.0) / num_in
    lat_out_ms_tok = (raw_lat_out * 1000.0) / num_out

    # Convert measured energy in kWh to Joules:
    # kWh * 3,600,000
    raw_energy_in = _to_numeric(raw[prefill_energy_col]) if (prefill_energy_col and prefill_energy_col in raw.columns) else pd.Series([np.nan]*len(raw), index=raw.index)
    raw_energy_out = _to_numeric(raw[decode_energy_col]) if (decode_energy_col and decode_energy_col in raw.columns) else pd.Series([np.nan]*len(raw), index=raw.index)

    energy_in_j = raw_energy_in * 3600000.0
    energy_out_j = raw_energy_out * 3600000.0

    out = pd.DataFrame(
        {
            "model_name": _to_text(raw[model_col]),
            "precision": _to_text(raw[precision_col]) if precision_col else "unknown",
            "num_input_tokens": num_in,
            "num_output_tokens": num_out,
            "latency_per_input_token_ms": lat_in_ms_tok,
            "latency_per_output_token_ms": lat_out_ms_tok,
            "prefill_energy_j": energy_in_j,
            "decode_energy_j": energy_out_j,
            "gpu_type": _to_text(raw[gpu_col]),
            "source_file": _to_text(raw["source_file"]),
            "_raw_lat_in": raw_lat_in,
            "_raw_lat_out": raw_lat_out,
        }
    )

    # Require latency + token count + model + GPU. Energy is synthesized from these.
    # Note: Latency measurements are sparse in the dataset (~40% coverage).
    # num_output_tokens is filled with default if missing, so don't filter on it.
    out = out.dropna(
        subset=[
            "model_name",
            "num_input_tokens",
            "latency_per_input_token_ms",
            "latency_per_output_token_ms",
            "gpu_type",
        ]
    )
    out = out[out["model_name"].str.len() > 0]

    # Filter to GPU rows only (energy synthesis needs a known TDP)
    _GPU_TDP_W: dict[str, float] = {
        "a100": 400.0,
        "a10": 150.0,
        "t4": 70.0,
        "v100": 300.0,
        "l4": 72.0,
        "l40": 300.0,
        "h100": 700.0,
        "a30": 165.0,
    }

    def _tdp_for_gpu(gpu_str: str) -> float | None:
        if not isinstance(gpu_str, str):
            return None
        g = gpu_str.lower()
        for key, tdp in _GPU_TDP_W.items():
            if key in g:
                return tdp
        return None

    out["_tdp_w"] = out["gpu_type"].apply(_tdp_for_gpu).astype("float64")
    out = out[out["_tdp_w"].notna()].copy()  # keep only known-GPU rows

    # Force numeric columns to float64 (CSV → Arrow dtype can cause multiplication errors)
    for _c in ["latency_per_input_token_ms", "latency_per_output_token_ms",
               "num_input_tokens", "num_output_tokens",
               "prefill_energy_j", "decode_energy_j"]:
        out[_c] = pd.to_numeric(out[_c], errors="coerce").astype("float64")

    # Synthesize energy where measurement is absent:
    missing_prefill = out["prefill_energy_j"].isna()
    missing_decode = out["decode_energy_j"].isna()
    
    out.loc[missing_prefill, "prefill_energy_j"] = (
        out.loc[missing_prefill, "_tdp_w"]
        * out.loc[missing_prefill, "_raw_lat_in"]
    )
    out.loc[missing_decode, "decode_energy_j"] = (
        out.loc[missing_decode, "_tdp_w"]
        * out.loc[missing_decode, "_raw_lat_out"]
    )
    
    out = out.drop(columns=["_tdp_w", "_raw_lat_in", "_raw_lat_out"])
    out = out.dropna(subset=["prefill_energy_j", "decode_energy_j"])

    meta = {
        "rows_raw": int(len(raw)),
        "rows_out": int(len(out)),
        "perf_files_count": len(used_files),
        "perf_files_sample": used_files[:20],
        "selected_columns": {
            "model_name": model_col,
            "precision": precision_col or "(filled=unknown)",
            "num_input_tokens": in_tok_col,
            "num_output_tokens": out_tok_col,
            "latency_per_input_token_ms": lat_in_col,
            "latency_per_output_token_ms": lat_out_col,
            "prefill_energy_j": prefill_energy_col,
            "decode_energy_j": decode_energy_col,
            "gpu_type": gpu_col,
        },
    }

    out_path = data_dir / "llm_perf_leaderboard.parquet"
    out.to_parquet(out_path, index=False)

    return out, meta


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    open_df, open_meta = build_open_llm_table(data_dir)
    perf_df, perf_meta = build_llm_perf_table(data_dir)

    verification = {
        "open_llm": open_meta,
        "llm_perf": perf_meta,
        "outputs": {
            "open_llm_path": str((data_dir / "open_llm_leaderboard.parquet")),
            "llm_perf_path": str((data_dir / "llm_perf_leaderboard.parquet")),
            "open_llm_columns": list(open_df.columns),
            "llm_perf_columns": list(perf_df.columns),
        },
    }

    verify_path = data_dir / "dataset_verification.json"
    verify_path.write_text(json.dumps(verification, indent=2), encoding="utf-8")

    print("Saved:")
    print(data_dir / "open_llm_leaderboard.parquet")
    print(data_dir / "llm_perf_leaderboard.parquet")
    print(data_dir / "dataset_verification.json")
    print(json.dumps(verification, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
