from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = PROJECT_ROOT / "swe-pruner" / "swe-pruner" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))


def _post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def offline_checks() -> None:
    from swe_pruner.carbon_estimator import CarbonEstimateRequest, CarbonEstimator
    from swe_pruner.repository.dependency_graph import DependencyGraph
    from swe_pruner.repository.repository_index import RepositoryIndex
    from swe_pruner.retrieval.graph_retriever import GraphRetriever

    estimator = CarbonEstimator()
    assert estimator.is_ready(), "carbon artifacts are not ready"
    short = estimator.estimate(
        CarbonEstimateRequest(
            input_tokens=512,
            output_tokens=128,
            model_name="meta-llama-3-8b-instruct",
        )
    )
    long = estimator.estimate(
        CarbonEstimateRequest(
            input_tokens=1024,
            output_tokens=128,
            model_name="meta-llama-3-8b-instruct",
        )
    )
    assert short.total_joules > 0
    assert long.prefill_joules > short.prefill_joules
    assert abs(long.prefill_joules / short.prefill_joules - 2.0) < 0.02

    demo = PROJECT_ROOT / "Test_project"
    index = RepositoryIndex(str(demo))
    index.build_index()
    assert "app.py" in index.index
    assert "services/auth_service.py" in index.index
    assert "services/payment_service.py" in index.index

    graph = DependencyGraph(index)
    graph.build_graph()
    distances = GraphRetriever(graph).get_neighbors({"app.py"}, max_hops=2)
    assert distances.get("services/auth_service.py") == 1
    assert distances.get("services/payment_service.py") == 1
    assert any(distance == 2 for distance in distances.values()), "expected a transitive dependency"

    print("OFFLINE_SMOKE_OK")
    print(f"carbon_512J={short.total_joules:.4f}")
    print(f"carbon_1024J={long.total_joules:.4f}")
    print(f"indexed_python_files={len(index.index)}")
    print(f"graph_candidates={len(distances)}")


def full_checks(base_url: str) -> None:
    health = _get_json(f"{base_url}/health")
    assert health.get("status") == "healthy", health
    assert health.get("model_loaded") is True, health
    assert health.get("carbon_models_loaded") is True, health

    carbon = _post_json(
        f"{base_url}/estimate-carbon",
        {
            "input_tokens": 1000,
            "output_tokens": 128,
            "model_name": "meta-llama-3-8b-instruct",
            "carbon_intensity_g_per_kwh": 475,
        },
    )
    assert carbon["total_joules"] > 0, carbon

    auth_code = (PROJECT_ROOT / "Test_project" / "services" / "auth_service.py").read_text(encoding="utf-8")
    prune = _post_json(
        f"{base_url}/prune",
        {
            "query": "Find account lockout and successful authentication logic.",
            "code": auth_code,
            "threshold": 0.45,
        },
    )
    assert prune["origin_token_cnt"] > 0, prune
    assert prune["left_token_cnt"] > 0, prune
    assert prune["left_token_cnt"] <= prune["origin_token_cnt"], prune
    assert prune["pruned_code"].strip(), prune

    demo = PROJECT_ROOT / "Test_project"
    workspace = _post_json(
        f"{base_url}/prune-workspace",
        {
            "query": "Trace authentication and payment processing from the application entrypoint.",
            "workspace_root": str(demo),
            "active_file": str(demo / "app.py"),
            "language": "python",
            "diagnostics": [],
            "threshold": 0.45,
            "token_budget": 4096,
        },
    )
    assert workspace["unified_prompt"].strip(), workspace
    assert workspace["pruned_tokens"] <= 4096, workspace
    assert workspace["files"], workspace
    assert any(item["tier"] == 1 for item in workspace["files"]), workspace

    print("FULL_SMOKE_OK")
    print(json.dumps({
        "health": health,
        "single_file": {
            "origin_tokens": prune["origin_token_cnt"],
            "pruned_tokens": prune["left_token_cnt"],
            "score": prune["score"],
        },
        "workspace": {
            "packed_tokens": workspace["pruned_tokens"],
            "files": len(workspace["files"]),
        },
        "carbon_total_joules": carbon["total_joules"],
    }, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--offline", action="store_true")
    group.add_argument("--full", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    try:
        if args.offline:
            offline_checks()
        else:
            full_checks(args.base_url.rstrip("/"))
    except (AssertionError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"SMOKE_TEST_FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
