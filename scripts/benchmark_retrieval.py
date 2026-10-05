"""Measure index/search overhead on temporary Python sources, without model inference."""

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "swe-pruner/swe-pruner/src"))

from swe_pruner.repository.repository_index import RepositoryIndexCache
from swe_pruner.retrieval.graph_retriever import GraphRetriever
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder


def distribution(samples: list[float]) -> dict:
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(sorted(samples)[math.ceil(len(samples) * 0.95) - 1], 3),
    }


def benchmark(files: int, queries: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="tokenwise-retrieval-benchmark-") as directory:
        root = Path(directory).resolve()
        sources = root / "services"
        sources.mkdir()
        for number in range(files):
            previous = (number - 1) % files
            content = (
                f"from services.module_{previous} import scenario_{previous}\n\n"
                f"def scenario_{number}(user: str, failures: int = 5):\n"
                '    """Account lockout policy after failed login attempts."""\n'
                f"    return {{'scenario': {number}, 'locked': failures >= 5}}\n"
            )
            (sources / f"module_{number}.py").write_text(content, encoding="utf-8")

        cache = RepositoryIndexCache(reconcile_seconds=3600, lease_seconds=3600)
        builder = WorkspaceContextBuilder()
        began = time.perf_counter()
        first = cache.synchronize(str(root), "benchmark", "start")
        builder.prepare(first)
        cold_ms = (time.perf_counter() - began) * 1000
        entry = cache.entries[str(root)]

        def search(number: int) -> None:
            snapshot, _ = cache.get(str(root))
            lexical, graph, reused = builder.prepare(snapshot)
            assert reused, "Unchanged queries rebuilt search data"
            matches = lexical.search_query(f"Explain account lockout scenario_{number % files}", limit=6)
            assert matches
            GraphRetriever(graph).get_neighbors({matches[0][0]}, max_hops=2)

        def measure() -> tuple[list[float], int, int]:
            timings = []
            with patch("swe_pruner.repository.repository_index.os.walk", wraps=os.walk) as walks, \
                 patch.object(entry.indexer, "index_file", wraps=entry.indexer.index_file) as parses:
                for number in range(queries):
                    began = time.perf_counter()
                    search(number)
                    timings.append((time.perf_counter() - began) * 1000)
                return timings, walks.call_count, parses.call_count

        warm, warm_walks, warm_parses = measure()
        assert warm_walks == warm_parses == 0, "Warm requests touched the repository"
        with patch.object(entry.indexer, "index_file", wraps=entry.indexer.index_file) as parses:
            changed = sources / "module_0.py"
            changed.write_text(first.index["services/module_0.py"]["content"] + "UPDATED_POLICY = True\n", encoding="utf-8")
            began = time.perf_counter()
            updated = cache.synchronize(str(root), "benchmark", "update", ["services/module_0.py"])
            builder.prepare(updated)
            update_ms = (time.perf_counter() - began) * 1000
            assert parses.call_count == 1, "A single edit reparsed unrelated sources"
            assert first.fingerprint != updated.fingerprint
            assert first.index["services/module_1.py"] is updated.index["services/module_1.py"]

        cache.synchronize(str(root), "benchmark", "stop")
        fallback, fallback_walks, fallback_parses = measure()
        assert fallback_walks == queries and fallback_parses == 0
        return {
            "scope": "Synthetic index + lexical search + graph expansion only; no neural pruning, HTTP, or Antigravity model calls",
            "files": files, "distinct_queries": queries, "cold_index_and_search_prepare_ms": round(cold_ms, 3),
            "watched": {**distribution(warm), "repository_walks": warm_walks, "ast_parses": warm_parses},
            "single_file_update_and_search_prepare": {"ms": round(update_ms, 3), "ast_parses": 1},
            "unwatched_conservative_fallback": {**distribution(fallback), "repository_walks": fallback_walks, "ast_parses": fallback_parses},
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", type=int, default=1000)
    parser.add_argument("--queries", type=int, default=50)
    args = parser.parse_args()
    if args.files < 2 or not 1 <= args.queries <= args.files:
        parser.error("Use at least 2 files and 1 <= queries <= files.")
    print(json.dumps(benchmark(args.files, args.queries), indent=2))


if __name__ == "__main__":
    main()
