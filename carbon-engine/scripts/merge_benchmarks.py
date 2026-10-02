from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_engine.io_utils import load_table, save_parquet
from carbon_engine.merge import merge_benchmark_tables, stats_to_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge LLM-Perf and Open LLM benchmark datasets.")
    parser.add_argument("--llm-perf", required=True, help="Path to LLM-Perf table (.csv or .parquet)")
    parser.add_argument("--open-llm", required=True, help="Path to Open LLM table (.csv or .parquet)")
    parser.add_argument("--output", required=True, help="Output parquet file path")
    parser.add_argument(
        "--stats-output",
        required=False,
        help="Optional JSON path where merge stats are written",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    llm_perf_df = load_table(args.llm_perf)
    open_llm_df = load_table(args.open_llm)

    merged_df, stats = merge_benchmark_tables(llm_perf_df, open_llm_df)
    save_parquet(merged_df, args.output)

    stats_payload = stats_to_dict(stats)
    if args.stats_output:
        stats_path = Path(args.stats_output)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(json.dumps(stats_payload, indent=2), encoding="utf-8")

    print(json.dumps(stats_payload, indent=2))
    print(f"Saved merged dataset to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
