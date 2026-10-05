"""Check the single teaching application; optionally export live context comparisons."""

import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent


def request(base: str, endpoint: str, payload: dict) -> dict:
    call = Request(base + endpoint, data=json.dumps(payload).encode("utf-8"),
                   headers={"Content-Type": "application/json"})
    with build_opener(ProxyHandler({})).open(call, timeout=120) as response:
        return json.load(response)


def cases() -> list[dict]:
    return json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]


def check_projects() -> list[dict]:
    results = []
    for case in cases():
        directory = (ROOT / case["project"]).resolve()
        if not directory.is_relative_to(ROOT) or not directory.is_dir():
            raise ValueError("Invalid demonstration project path")
        tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                               cwd=directory, capture_output=True, text=True, encoding="utf-8", check=True)
        app = subprocess.run([sys.executable, "app.py"], cwd=directory, capture_output=True,
                             text=True, encoding="utf-8", check=True)
        count = int(re.search(r"Ran (\d+) tests?", tests.stderr).group(1))
        print(f"{case['project']}: {count} tests passed; app.py passed", flush=True)
        results.append({"project": case["project"], "tests_passed": count, "app_output": app.stdout})
    return results


def compare_projects(base: str, output: Path, budget: int = 4096) -> list[dict]:
    url = urlparse(base)
    if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost", "::1"} or url.username or url.password \
            or url.path not in {"", "/"} or url.query or url.fragment:
        raise ValueError("Use the local TokenWise backend URL")
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in cases():
        directory = (ROOT / case["project"]).resolve()
        print(f"Retrieving real context: {case['project']}", flush=True)
        started = time.perf_counter()
        result = request(base, "/compare-workspace", {
            "workspace_root": str(directory), "selection_file": case["selection_file"],
            "query": case["query"], "token_budget": budget, "max_candidates": 8,
        })
        elapsed = round(time.perf_counter() - started, 3)
        comparison = result["comparison"]
        assert result["pruned_tokens"] <= budget
        methods = comparison["methods"]
        assert [item["id"] for item in methods] == ["all_python", "selected", "tokenwise"]
        native = subprocess.run(["node", str(PROJECT / "scripts/verify-carbon-client.cjs")],
                                input=json.dumps({"base": base, "inputs": [item["input_tokens"] for item in methods]}),
                                cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", timeout=40, check=True)
        estimates = json.loads(native.stdout)
        for method, carbon in zip(methods, estimates):
            method["carbon"] = carbon
            present = [marker for marker in case["evidence_markers"] if marker in method["context"]]
            rows.append({"project": case["project"], "strategy": method["id"], "input_tokens": method["input_tokens"],
                         "files": len(method["files"]), "evidence_markers_present": len(present),
                         "evidence_markers_total": len(case["evidence_markers"]), "estimated_co2_g": carbon["co2Grams"],
                         "comparison_retrieval_seconds": elapsed, "agent_answer_scored": False})
            method["evidence_markers_present"] = present
        comparison["carbonStatus"] = "ready"
        comparison["notes"].append("Fixed scenario: Llama-3 8B, 256 expected output tokens, 475 gCO2/kWh. Marker presence is not answer correctness.")
        folder = output / case["project"]
        folder.mkdir(exist_ok=True)
        (folder / "comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        for method in methods:
            (folder / f"{method['id']}.md").write_text(method["context"], encoding="utf-8", newline="\n")
        print(f"Saved actual comparisons for {case['project']}: {[item['input_tokens'] for item in methods]}", flush=True)
    with (output / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", help="Optional actual local backend URL for live comparisons.")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    check_projects()
    if args.api_url:
        compare_projects(args.api_url.rstrip("/"), args.output.resolve())


if __name__ == "__main__":
    main()
