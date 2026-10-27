#!/usr/bin/env python3
"""Re-score archived OpenClaw hard-suite responses with a versioned profile."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from openclaw_hosted_model_suite import apply_evaluation_profile  # noqa: E402
from openclaw_local_model_suite import score_case  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE = ROOT / "configs" / "benchmarks" / "openrouter-budget-reference-v2-20261016.json"
DEFAULT_RUNS_DIR = ROOT / "docs" / "benchmarks" / "runs"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "benchmarks" / "archive-rescore-20261016"


def rescore_result(
    result: dict[str, Any],
    case_by_id: dict[str, dict[str, Any]],
    run_id: str,
    source_path: Path,
) -> dict[str, Any]:
    cases = result.get("cases", [])
    rescored_cases: list[dict[str, Any]] = []
    for case in cases:
        case_id = case.get("id")
        response = str(case.get("response", "") or "")
        updated = score_case(case_by_id[case_id], response) if case_id in case_by_id and response else None
        rescored_cases.append(
            {
                "id": case_id,
                "old_score": case.get("score"),
                "contract_v2_score": updated["score"] if updated else None,
                "has_response": bool(response.strip()),
                "finish_reason": case.get("finish_reason"),
                "error": case.get("error"),
            }
        )

    ids = {case.get("id") for case in cases}
    valid_v2 = [case for case in rescored_cases if case["contract_v2_score"] is not None]
    complete = len(cases) == 28 and len(ids) == 28 and len(valid_v2) == 28
    old_scores = [float(case.get("score", 0)) for case in cases]
    old_score = sum(old_scores) / len(old_scores) if old_scores else None
    v2_score = (
        sum(float(case["contract_v2_score"]) for case in valid_v2) / len(valid_v2)
        if valid_v2
        else None
    )
    return {
        "run_id": run_id,
        "model": result.get("model"),
        "path": result.get("path"),
        "source_path": str(source_path.relative_to(ROOT)),
        "total_cases": len(cases),
        "unique_cases": len(ids),
        "responses": sum(1 for case in rescored_cases if case["has_response"]),
        "complete_hard28": complete,
        "old_score_pct": round(old_score * 100, 4) if old_score is not None else None,
        "contract_v2_score_pct": round(v2_score * 100, 4) if v2_score is not None else None,
        "delta_pct_points": round((v2_score - old_score) * 100, 4)
        if old_score is not None and v2_score is not None
        else None,
        "finish_length_count": sum(1 for case in cases if case.get("finish_reason") == "length"),
        "errors": sum(1 for case in cases if case.get("error")),
        "cases": rescored_cases,
    }


def collect_results(runs_dir: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    suite_path = ROOT / profile["suite"]
    suite = apply_evaluation_profile(json.loads(suite_path.read_text(encoding="utf-8")), profile)
    case_by_id = {case["id"]: case for case in suite["cases"]}
    rows: list[dict[str, Any]] = []
    for source_path in sorted(runs_dir.glob("*/openclaw_local_model_suite_results.json")):
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        if payload.get("suite", {}).get("suite_id") != "openclaw_local_model_suite_hard_v1":
            continue
        for result in payload.get("results", []):
            rows.append(rescore_result(result, case_by_id, source_path.parent.name, source_path))
    return rows


def write_reports(output_dir: Path, profile: dict[str, Any], results: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "profile_id": profile.get("profile_id"),
        "results": results,
    }
    (output_dir / "archive_rescore_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary_fields = [
        "run_id",
        "model",
        "complete_hard28",
        "total_cases",
        "responses",
        "old_score_pct",
        "contract_v2_score_pct",
        "delta_pct_points",
        "finish_length_count",
        "errors",
        "source_path",
    ]
    with (output_dir / "archive_rescore_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in summary_fields} for row in results)

    complete = [row for row in results if row["complete_hard28"]]
    incomplete = [row for row in results if not row["complete_hard28"]]
    complete.sort(key=lambda row: row["contract_v2_score_pct"], reverse=True)
    lines = [
        "# Archived OpenClaw hard-suite re-score",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Evaluation profile: `{profile.get('profile_id')}`",
        f"Complete 28-case runs: **{len(complete)}**",
        f"Incomplete or partial entries: **{len(incomplete)}**",
        "",
        "This is an offline deterministic contract re-score of saved responses. Models were not run again.",
        "Semantic v2 is not inferred where no semantic judge was executed.",
        "",
        "## Complete runs",
        "",
        "| Rank | Model | Source run | Old | Contract v2 | Delta | Length |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(complete, 1):
        lines.append(
            f"| {rank} | `{row['model']}` | `{row['run_id']}` | {row['old_score_pct']:.2f}% | "
            f"{row['contract_v2_score_pct']:.2f}% | {row['delta_pct_points']:+.2f} pp | "
            f"{row['finish_length_count']} |"
        )
    lines.extend(
        [
            "",
            "## Incomplete entries",
            "",
            "| Model | Source run | Cases | Responses |",
            "|---|---|---:|---:|",
        ]
    )
    for row in incomplete:
        lines.append(
            f"| `{row['model']}` | `{row['run_id']}` | {row['total_cases']} | {row['responses']} |"
        )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    results = collect_results(Path(args.runs_dir), profile)
    write_reports(Path(args.output_dir), profile, results)
    complete = sum(1 for row in results if row["complete_hard28"])
    print(f"Re-scored {complete} complete runs; {len(results) - complete} incomplete entries", flush=True)
    print(f"Report: {Path(args.output_dir) / 'README.md'}", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
