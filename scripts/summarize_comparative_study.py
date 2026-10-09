"""Derive descriptive statistics and report tables from actual saved measurements."""

import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "evaluation/comparative-study"


def distribution(values):
    return {"min": min(values), "median": statistics.median(values), "mean": statistics.mean(values), "max": max(values)}


def main():
    report = json.loads((DATA / "results.json").read_text(encoding="utf-8"))
    snapshots = json.loads((DATA / "snapshots.json").read_text(encoding="utf-8"))
    if len(report["results"]) != 20 or report["failures"] or not report.get("run_finished_utc"):
        raise ValueError("A completed twenty-repository run with no failures is required")
    cases = report["results"]
    rows = [row for case in cases for row in case["rows"]]
    grouped = {name: [row for row in rows if row["strategy"] == name] for name in {row["strategy"] for row in rows}}
    by_case = {case["repository"]: {row["strategy"]: row for row in case["rows"]} for case in cases}
    summary = {"repositories": 20, "packet_conditions": len(rows), "indexed_python_files": sum(case["indexed_python_files"] for case in cases),
               "indexed_source_bytes": sum(snapshots[case["repository"]]["indexed_source_bytes"] for case in cases),
               "required_evidence_items": sum(case["rows"][0]["evidence_total"] for case in cases),
               "excerpt_clipped_cases": sum(case["excerpt_clipped"] for case in cases),
               "strategies": {}, "neural_seconds": distribution([case["neural_excerpt_seconds"] for case in cases]),
               "index_prepare_seconds": distribution([case["index_and_search_prepare_seconds"] for case in cases]),
               "warm_search_seconds": distribution([case["warm_search_median_seconds"] for case in cases])}
    baseline_total = sum(row["input_tokens"] for row in grouped["all_python"])
    for name, group in grouped.items():
        tokens = sum(row["input_tokens"] for row in group)
        summary["strategies"][name] = {
            "input_tokens": distribution([row["input_tokens"] for row in group]), "total_input_tokens": tokens,
            "aggregate_reduction_vs_all_python_pct": 100 * (baseline_total - tokens) / baseline_total,
            "mean_per_repository_reduction_vs_all_python_pct": statistics.mean([
                100 * (by_case[row["repository"]]["all_python"]["input_tokens"] - row["input_tokens"]) /
                by_case[row["repository"]]["all_python"]["input_tokens"] for row in group]),
            "evidence_retained": sum(row["evidence_retained"] for row in group),
            "macro_evidence_recall_pct": 100 * statistics.mean(row["evidence_recall"] for row in group),
            "required_files_retrieved": sum(row["required_files_retrieved"] for row in group),
            "required_files_total": sum(row["required_files_total"] for row in group),
            "estimated_total_co2_g": sum(row["carbon"]["co2_grams"] for row in group),
            "budget_violations_4096": sum(row["input_tokens"] > 4096 for row in group)}
    before = summary["strategies"]["selected_excerpt"]
    after = summary["strategies"]["neural_excerpt"]
    changes = [100 * (methods["selected_excerpt"]["input_tokens"] - methods["neural_excerpt"]["input_tokens"]) /
               methods["selected_excerpt"]["input_tokens"] for methods in by_case.values()]
    summary["matched_neural_comparison"] = {
        "packet_reduction_pct": 100 * (before["total_input_tokens"] - after["total_input_tokens"]) / before["total_input_tokens"],
        "per_case_reduction_pct": distribution(changes), "cases_smaller": sum(value > 0 for value in changes),
        "cases_equal": sum(value == 0 for value in changes), "cases_larger": sum(value < 0 for value in changes),
        "source_tokens_before": sum(case["excerpt_source_tokens"] for case in cases),
        "source_tokens_after": sum(case["neural_source_tokens"] for case in cases),
        "estimated_co2_saved_g": before["estimated_total_co2_g"] - after["estimated_total_co2_g"],
        "estimated_co2_reduction_pct": 100 * (before["estimated_total_co2_g"] - after["estimated_total_co2_g"]) / before["estimated_total_co2_g"]}
    differences = [methods["history_on"]["required_files_retrieved"] - methods["history_off"]["required_files_retrieved"] for methods in by_case.values()]
    summary["memory_comparison"] = {
        "required_file_coverage_improved_cases": sum(value > 0 for value in differences),
        "required_file_coverage_equal_cases": sum(value == 0 for value in differences),
        "required_file_coverage_worse_cases": sum(value < 0 for value in differences),
        "off_clarification_cases": sum(methods["history_off"]["clarification_required"] is True for methods in by_case.values()),
        "on_clarification_cases": sum(methods["history_on"]["clarification_required"] is True for methods in by_case.values()),
        "on_hint_used_cases": sum(methods["history_on"]["context_hint_used"] is True for methods in by_case.values())}
    (DATA / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    tables = ["# Generated Measurement Tables", "", "Generated by `scripts/summarize_comparative_study.py`; not hand-entered results.", "",
              "## Context Sizes and Evidence", "",
              "| Repository | Python files | All Python | Selected file | Excerpt before | Neural after | Matched reduction | Neural evidence | Retrieval-only |", 
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for case in cases:
        name = case["repository"]
        methods = by_case[name]
        pre = methods["selected_excerpt"]["input_tokens"]
        post = methods["neural_excerpt"]["input_tokens"]
        neural = methods["neural_excerpt"]
        tables.append(f"| [{name}]({snapshots[name]['source_url']}) | {case['indexed_python_files']} | {methods['all_python']['input_tokens']:,} | {methods['selected_file']['input_tokens']:,} | {pre} | {post} | {100*(pre-post)/pre:.2f}% | {neural['evidence_retained']}/{neural['evidence_total']} | {methods['retrieval_only']['input_tokens']} |")
    tables += ["", "## Conversation Memory Ablation (Retrieval Only)", "",
               "| Repository | Off tokens | On tokens | Off required files | On required files | Off body anchors | On body anchors |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for case in cases:
        off, on = (by_case[case["repository"]][name] for name in ("history_off", "history_on"))
        tables.append(f"| {case['repository']} | {off['input_tokens']} | {on['input_tokens']} | {off['required_files_retrieved']}/{off['required_files_total']} | {on['required_files_retrieved']}/{on['required_files_total']} | {off['evidence_retained']}/{off['evidence_total']} | {on['evidence_retained']}/{on['evidence_total']} |")
    tables += ["", "## Exact Source Pins", "", "| Repository | Tag | Commit |", "|---|---|---|"]
    for case in cases:
        name = case["repository"]
        pin = snapshots[name]
        tables.append(f"| [{name}]({pin['source_url']}) | `{pin['ref']}` | `{pin['commit']}` |")
    (DATA / "tables.md").write_text("\n".join(tables) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
