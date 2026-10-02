from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CarbonEnginePaths:
    root: Path
    data_dir: Path
    artifacts_dir: Path

    @property
    def llm_perf_path(self) -> Path:
        return self.data_dir / "llm_perf_leaderboard.parquet"

    @property
    def open_llm_path(self) -> Path:
        return self.data_dir / "open_llm_leaderboard.parquet"

    @property
    def merged_path(self) -> Path:
        return self.data_dir / "seal_training_dataset.parquet"


def get_default_paths(root: str | Path | None = None) -> CarbonEnginePaths:
    root_path = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    return CarbonEnginePaths(
        root=root_path,
        data_dir=root_path / "data",
        artifacts_dir=root_path / "artifacts",
    )
