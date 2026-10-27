#!/usr/bin/env python3
"""Re-score archived Bunker Benchmark v3 runs with the v3.1 semantic rubric.

The command never calls candidate models and never mutates archived result
files.  It reuses their final answers and traces, preserves strict structural
and agent-execution checks, and replaces only the literal checks listed in the
versioned rubric.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "scripts" / "benchmarking" / "bunker_benchmark_v3.py"
DEFAULT_SUITE = ROOT / "scripts" / "benchmarking" / "corpora" / "bunker_benchmark_v3.json"
DEFAULT_RUBRIC = (
    ROOT
    / "scripts"
    / "benchmarking"
    / "corpora"
    / "bunker_benchmark_v3_1_semantic_rubric.json"
)


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("bunker_benchmark_v3_rescore_runtime", RUNNER_PATH)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot import benchmark runner from {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return value


def apply_rubric(suite: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(suite)
    if rubric.get("base_suite_id") != suite.get("suite_id"):
        raise ValueError(
            f"Rubric expects {rubric.get('base_suite_id')}, got {suite.get('suite_id')}"
        )
    by_id = {case["id"]: case for case in updated["cases"]}
    for case_id, replacements in rubric.get("cases", {}).items():
        if case_id not in by_id:
            raise ValueError(f"Rubric references unknown case {case_id}")
        checks = by_id[case_id]["checks"]
        for replacement in replacements:
            index = int(replacement["index"]) - 1
            if index < 0 or index >= len(checks):
                raise ValueError(f"{case_id}: replacement index {index + 1} is out of range")
            old_label = checks[index].get("label")
            new_label = replacement["check"].get("label")
            if old_label and new_label and old_label != new_label:
                raise ValueError(
                    f"{case_id}: replacement changes label {old_label!r} to {new_label!r}"
                )
            checks[index] = replacement["check"]
    updated["evaluation_version"] = rubric["evaluation_version"]
    updated["semantic_rubric_id"] = rubric["rubric_id"]
    errors = RUNNER.validate_suite(updated)
    if errors:
        raise ValueError("Invalid rescoring suite: " + "; ".join(errors))
    return updated


def original_check_passed(case: dict[str, Any], check_type: str) -> bool | None:
    for check in case.get("checks", []):
        if check.get("type") == check_type:
            return bool(check.get("passed"))
    return None


def run_fingerprint(run: dict[str, Any]) -> str:
    stable = {
        "model": run.get("model"),
        "cases": [
            {
                "id": case.get("id"),
                "answer": case.get("answer"),
                "raw_responses": case.get("raw_responses"),
                "trace": case.get("trace"),
                "finish_reasons": case.get("finish_reasons"),
            }
            for case in run.get("cases", [])
        ],
    }
    encoded = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def source_is_canonical(source: str) -> bool:
    lowered = source.lower()
    if "tool-compat" in lowered or "smoke" in lowered:
        return False
    return any(
        marker in lowered
        for marker in (
            "bunker-v3-qwen38-lowquants-20261027",
            "bunker-v3-russian-vendors-20261027",
            "bunker-v3-heretic-q6-q8-20261027",
            "bunker-v3-q8-unchained-retest-20261027",
            "bunker-v3-q8-repair-20261027",
            "bunker-v3-ornith-bolt-20261027",
            "bunker-v3-nemotron-bolt-iq4xs-20261028",
            "bunker-v3-q8-leaders-20261027",
            "bunker-v3-october-wave-20261026",
            "bunker-v3-medium-large-20261019",
            "bunker-v3-small-local-20261018",
            "bunker-benchmark-v3-small-local-20261018",
            "bunker-benchmark-v3-small-medium-20261018",
            "bunker-benchmark-v3-hosted-20261018",
        )
    )


def source_priority(source: str) -> int:
    lowered = source.lower()
    if any(
        marker in lowered
        for marker in (
            "bunker-v3-ornith-bolt-20261027",
            "bunker-v3-nemotron-bolt-iq4xs-20261028",
        )
    ):
        return 90
    if "bunker-v3-q8-repair-20261027" in lowered:
        return 80
    if any(
        marker in lowered
        for marker in (
            "bunker-v3-qwen38-lowquants-20261027",
            "bunker-v3-russian-vendors-20261027",
            "bunker-v3-heretic-q6-q8-20261027",
            "bunker-v3-q8-unchained-retest-20261027",
            "bunker-v3-q8-leaders-20261027",
        )
    ):
        return 70
    if "bunker-v3-october-wave-20261026" in lowered:
        return 50
    if "bunker-benchmark-v3-hosted-20261018" in lowered:
        return 45
    if "vulkan-fullgpu" in lowered:
        return 40
    if "bunker-v3-medium-large-20261019" in lowered:
        return 30
    if "bunker-benchmark-v3-small-medium-20261018" in lowered:
        return 20
    if "bunker-v3-small-local-20261018" in lowered:
        return 10
    return 0


def rescore_case(case: dict[str, Any], case_spec: dict[str, Any]) -> dict[str, Any]:
    final_answer_passed = original_check_passed(case, "final_answer_present")
    completed = final_answer_passed if final_answer_passed is not None else bool(case.get("answer", "").strip())
    response = "\n".join(
        RUNNER.strip_orphan_reasoning_closers(str(item))
        for item in case.get("raw_responses", [])
    )
    answer = RUNNER.strip_orphan_reasoning_closers(str(case.get("answer", "")))
    rescored = RUNNER.score_case(
        case_spec,
        response,
        answer,
        case.get("trace", []),
        completed=completed,
        truncated=bool(case.get("truncated")),
    )
    old_checks = case.get("checks", [])
    changed: list[dict[str, Any]] = []
    for index, new_check in enumerate(rescored["checks"]):
        old_check = old_checks[index] if index < len(old_checks) else {}
        old_passed = old_check.get("passed")
        if old_passed is not None and bool(old_passed) != bool(new_check.get("passed")):
            changed.append(
                {
                    "index": index + 1,
                    "label": new_check.get("label") or old_check.get("label"),
                    "old_type": old_check.get("type"),
                    "new_type": new_check.get("type"),
                    "old_passed": bool(old_passed),
                    "new_passed": bool(new_check.get("passed")),
                }
            )
    return {
        "id": case["id"],
        "track": case["track"],
        "score": rescored["score"],
        "raw_score": rescored["raw_score"],
        "critical_failures": rescored["critical_failures"],
        "checks": rescored["checks"],
        "changed_checks": changed,
        "truncated": bool(case.get("truncated")),
        "trace": case.get("trace", []),
        "repair_attempted": bool(case.get("repair_attempted")),
        "tool_call_source_formats": case.get("tool_call_source_formats", []),
        "latency_s": float(case.get("latency_s", 0) or 0),
    }


def discover_files(inputs: list[str]) -> list[tuple[str, str, Path]]:
    discovered: list[tuple[str, str, Path]] = []
    for raw in inputs:
        if "=" in raw:
            label, path_text = raw.split("=", 1)
        else:
            path_text = raw
            label = Path(path_text).name
        path = Path(path_text).expanduser().resolve()
        if path.is_file():
            discovered.append((label, path.name, path))
        elif path.is_dir():
            discovered.extend(
                (label, str(item.relative_to(path)), item)
                for item in sorted(path.rglob("benchmark_v3_results.json"))
            )
        else:
            raise FileNotFoundError(path)
    return discovered


def apply_source_exclusions(
    files: list[tuple[str, str, Path]], publication_config: str | None
) -> tuple[list[tuple[str, str, Path]], list[dict[str, str]]]:
    """Apply the same file-level exclusions used by the public result bundle."""
    if not publication_config:
        return files, []
    config = load_json(Path(publication_config))
    rules = config.get("exclusions", [])
    included: list[tuple[str, str, Path]] = []
    excluded: list[dict[str, str]] = []
    for label, source_path, result_path in files:
        normalized = source_path.replace("\\", "/")
        rule = next(
            (
                item
                for item in rules
                if str(item.get("path_contains", "")).replace("\\", "/") in normalized
            ),
            None,
        )
        if rule:
            excluded.append(
                {
                    "source": f"{label}:{source_path}",
                    "reason": str(rule.get("reason", "Excluded by publication policy.")),
                }
            )
        else:
            included.append((label, source_path, result_path))
    return included, excluded


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def summarize_models(runs: list[dict[str, Any]], representative: bool) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        if representative and not run["canonical"]:
            continue
        grouped[run["model"]].append(run)
    rows = []
    for model, model_runs in grouped.items():
        selected = model_runs
        if representative:
            best_priority = max(run["source_priority"] for run in model_runs)
            selected = [run for run in model_runs if run["source_priority"] == best_priority]
        original = [float(run["original_summary"]["capability_mean_pct"]) for run in selected]
        rescored = [float(run["v3_1_summary"]["capability_mean_pct"]) for run in selected]
        critical = [int(run["v3_1_summary"]["critical_failures"]) for run in selected]
        latencies = [float(run["latency_s"]) for run in selected]
        rows.append(
            {
                "model": model,
                "runs": len(selected),
                "source_priority": max(run["source_priority"] for run in selected),
                "original_mean_pct": round(mean(original), 2),
                "v3_1_mean_pct": round(mean(rescored), 2),
                "v3_1_min_pct": round(min(rescored), 2),
                "v3_1_max_pct": round(max(rescored), 2),
                "delta_pp": round(mean(rescored) - mean(original), 2),
                "critical_mean": round(mean([float(value) for value in critical]), 2),
                "critical_min": min(critical),
                "critical_max": max(critical),
                "eligible_runs": sum(
                    1 for run in selected if bool(run["v3_1_summary"]["eligible"])
                ),
                "latency_mean_s": round(mean(latencies), 2),
                "sources": sorted({run["source"] for run in selected}),
            }
        )
    rows.sort(key=lambda row: (row["v3_1_mean_pct"], -row["critical_mean"]), reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def write_report(path: Path, payload: dict[str, Any]) -> None:
    audit = payload["audit"]
    ranking = payload["representative_ranking"]
    changes = payload["changed_check_counts"]
    lines = [
        "# Bunker Benchmark v3.1: semantic re-evaluation",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Rubric: `{payload['rubric_id']}`",
        "",
        "## Outcome",
        "",
        f"Scanned **{audit['input_files']}** archived result files and **{audit['complete_runs']}** complete 20-case runs. "
        f"After removing byte-equivalent duplicate runs, **{audit['unique_complete_runs']}** runs across "
        f"**{audit['models']}** model configurations were re-scored. "
        f"The new rubric changed **{audit['failed_to_pass_checks']}** formerly failed literal checks to pass "
        f"after accepting equivalent wording, and changed **{audit['pass_to_failed_checks']}** passes to failures.",
        "",
        "The candidate answers were not regenerated. Empty leading reasoning close delimiters emitted by "
        "some chat templates were normalized as transport residue; complete reasoning blocks remain visible "
        "and fail the deterministic leak check. Tool selection, call arguments, parallelism, ordering, "
        "approval, exact evidence IDs, numeric values, JSON contracts, truncation and visible-reasoning checks "
        "remain deterministic. Only explicitly versioned free-text checks now accept equivalent Russian and "
        "English formulations and stable technical aliases.",
        "",
        "## Representative ranking",
        "",
        "For each model configuration, this table selects the newest canonical cohort available: verified "
        "2026-10-27 quantization and vendor cohorts first, then the October wave, hosted/full-GPU corrected "
        "runs, and the original medium/large wave. Diagnostic smoke and tool-compat runs remain in the audit "
        "JSON but are excluded here.",
        "",
        "| Rank | Model | Runs | v3.1 mean | Range | Old v3 | Delta | Critical failures | Eligible | Mean latency |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ranking:
        score_range = (
            f"{row['v3_1_min_pct']:.2f}%"
            if row["v3_1_min_pct"] == row["v3_1_max_pct"]
            else f"{row['v3_1_min_pct']:.2f}–{row['v3_1_max_pct']:.2f}%"
        )
        critical_range = (
            str(row["critical_min"])
            if row["critical_min"] == row["critical_max"]
            else f"{row['critical_min']}–{row['critical_max']}"
        )
        lines.append(
            f"| {row['rank']} | `{row['model']}` | {row['runs']} | {row['v3_1_mean_pct']:.2f}% | "
            f"{score_range} | {row['original_mean_pct']:.2f}% | {row['delta_pp']:+.2f} pp | "
            f"{critical_range} | {row['eligible_runs']}/{row['runs']} | {row['latency_mean_s']:.2f} s |"
        )
    if ranking:
        leader = ranking[0]
        repeated = [row for row in ranking if row["runs"] >= 3]
        repeated_leader = repeated[0] if repeated else None
        lines.extend(
            [
                "",
                f"The current representative leader is `{leader['model']}` at "
                f"**{leader['v3_1_mean_pct']:.2f}%** across {leader['runs']} run(s).",
            ]
        )
        if repeated_leader:
            lines.append(
                f"The highest-ranked repeated cohort is `{repeated_leader['model']}` at "
                f"**{repeated_leader['v3_1_mean_pct']:.2f}%** across {repeated_leader['runs']} runs "
                f"({repeated_leader['eligible_runs']}/{repeated_leader['runs']} eligible)."
            )
        lines.append(
            "Capability score and production eligibility are separate: any critical failure keeps a run "
            "out of the eligible set even when its mean score is high."
        )
    lines.extend(
        [
            "",
            "## Where the old scorer was brittle",
            "",
            "| Case / check | Failed → passed | Passed → failed |",
            "|---|---:|---:|",
        ]
    )
    for item in changes:
        lines.append(
            f"| `{item['case_id']}` / `{item['label']}` | {item['failed_to_pass']} | {item['pass_to_failed']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- v3.1 is a new evaluation version; it does not overwrite the published v3 result files.",
            "- Score changes mean the evaluator changed, not the models or their latency.",
            "- Repeated runs remain separate observations. Exact duplicate copies are counted once.",
            "- Incomplete runs are listed in the audit JSON and excluded from all scores.",
            "- The complete per-run and per-case audit is stored in the companion JSON file.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    suite = load_json(Path(args.suite))
    rubric = load_json(Path(args.rubric))
    rescoring_suite = apply_rubric(suite, rubric)
    case_specs = {case["id"]: case for case in rescoring_suite["cases"]}
    discovered_files = discover_files(args.input)
    files, excluded_files = apply_source_exclusions(
        discovered_files, args.publication_config
    )
    seen: set[str] = set()
    output_runs: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    duplicate_runs = 0
    complete_runs = 0
    changed_counts: Counter[tuple[str, str, str]] = Counter()

    for label, source_path, result_path in files:
        payload = load_json(result_path)
        for archived_run in payload.get("runs", []):
            cases = archived_run.get("cases", [])
            source = f"{label}:{source_path}"
            if len(cases) != len(case_specs) or {case.get("id") for case in cases} != set(case_specs):
                incomplete.append(
                    {
                        "source": source,
                        "model": archived_run.get("model"),
                        "run": archived_run.get("run"),
                        "case_count": len(cases),
                    }
                )
                continue
            complete_runs += 1
            fingerprint = run_fingerprint(archived_run)
            if fingerprint in seen:
                duplicate_runs += 1
                continue
            seen.add(fingerprint)
            rescored_cases = [rescore_case(case, case_specs[case["id"]]) for case in cases]
            for case in rescored_cases:
                for changed in case["changed_checks"]:
                    direction = "failed_to_pass" if changed["new_passed"] else "pass_to_failed"
                    changed_counts[(case["id"], str(changed.get("label") or changed["new_type"]), direction)] += 1
            original_summary = RUNNER.aggregate(cases)
            new_summary = RUNNER.aggregate(rescored_cases)
            compact_cases = []
            for original_case, rescored_case in zip(cases, rescored_cases):
                compact_cases.append(
                    {
                        "id": rescored_case["id"],
                        "track": rescored_case["track"],
                        "original_score": float(original_case.get("score", 0)),
                        "v3_1_score": rescored_case["score"],
                        "original_critical_failures": original_case.get(
                            "critical_failures", []
                        ),
                        "v3_1_critical_failures": rescored_case["critical_failures"],
                        "changed_checks": rescored_case["changed_checks"],
                    }
                )
            output_runs.append(
                {
                    "fingerprint": fingerprint,
                    "source": source,
                    "canonical": source_is_canonical(source),
                    "source_priority": source_priority(source),
                    "model": archived_run.get("model", "unknown"),
                    "run": archived_run.get("run"),
                    "latency_s": round(sum(float(case.get("latency_s", 0) or 0) for case in cases), 4),
                    "original_summary": original_summary,
                    "v3_1_summary": new_summary,
                    "cases": compact_cases,
                }
            )

    failed_to_pass = sum(value for (case, label, direction), value in changed_counts.items() if direction == "failed_to_pass")
    pass_to_failed = sum(value for (case, label, direction), value in changed_counts.items() if direction == "pass_to_failed")
    change_rows = []
    keys = sorted({(case, label) for case, label, direction in changed_counts})
    for case_id, label in keys:
        change_rows.append(
            {
                "case_id": case_id,
                "label": label,
                "failed_to_pass": changed_counts[(case_id, label, "failed_to_pass")],
                "pass_to_failed": changed_counts[(case_id, label, "pass_to_failed")],
            }
        )
    change_rows.sort(key=lambda row: (row["failed_to_pass"] + row["pass_to_failed"], row["case_id"]), reverse=True)

    result = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "base_suite_id": suite["suite_id"],
        "rubric_id": rubric["rubric_id"],
        "evaluation_version": rubric["evaluation_version"],
        "response_normalization": RUNNER.RESPONSE_NORMALIZATION_VERSION,
        "audit": {
            "input_files": len(files),
            "discovered_input_files": len(discovered_files),
            "excluded_input_files": len(excluded_files),
            "complete_runs": complete_runs,
            "unique_complete_runs": len(output_runs),
            "duplicate_runs": duplicate_runs,
            "incomplete_runs": len(incomplete),
            "models": len({run["model"] for run in output_runs}),
            "failed_to_pass_checks": failed_to_pass,
            "pass_to_failed_checks": pass_to_failed,
        },
        "changed_check_counts": change_rows,
        "representative_ranking": summarize_models(output_runs, representative=True),
        "all_run_model_summary": summarize_models(output_runs, representative=False),
        "incomplete_runs": incomplete,
        "excluded_input_files": excluded_files,
        "runs": output_runs,
    }
    output_json = Path(args.output_json)
    output_report = Path(args.output_report)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output_report, result)
    print(json.dumps(result["audit"], ensure_ascii=False, indent=2))
    print(f"JSON: {output_json}")
    print(f"Report: {output_report}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default=str(DEFAULT_SUITE))
    parser.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    parser.add_argument("--input", action="append", required=True, help="[label=]file-or-directory")
    parser.add_argument(
        "--publication-config",
        help="Optional publication config whose path_contains rules exclude superseded files.",
    )
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-report", required=True)
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
