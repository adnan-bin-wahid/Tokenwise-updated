from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".parquet"}


def load_table(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if file_path.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension for {file_path}")

    if file_path.suffix == ".csv":
        return pd.read_csv(file_path)

    return pd.read_parquet(file_path)


def save_parquet(df: pd.DataFrame, path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(file_path, index=False)
