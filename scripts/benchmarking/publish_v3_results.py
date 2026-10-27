#!/usr/bin/env python3
"""Build a sanitized, auditable publication bundle from Bunker v3 result files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path
from typing import Any


PRIVATE_IPV4 = re.compile(r"(?<![0-9])(?:10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}|192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.)[0-9]{1,3})(?![0-9])")
MAC_HOME = re.compile(r"/Users/[A-Za-z0-9._-]+/")
LINUX_BENCHMARK_HOME = re.compile(r"/home/[A-Za-z0-9._-]+/")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sanitize_string(value: str) -> str:
    linux_home = LINUX_BENCHMARK_HOME.search(value)
    if linux_home:
        home = linux_home.group()
        replacements = (
            (home + "bunker-evals-v3/", ""),
            (home + "bunker-data/", "<bunker-data>/"),
            (home + "releases/media/", "<release-media>/"),
            (home, "<benchmark-home>/"),
        )
        for old, new in replacements:
            value = value.replace(old, new)
    value = MAC_HOME.sub("<local-home>/", value)
    return PRIVATE_IPV4.sub("192.0.2.20", value)


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_string(value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    return value


def discover(inputs: list[Path]) -> list[tuple[Path, str]]:
    discovered: list[tuple[Path, str]] = []
    for root in inputs:
        root = root.resolve()
        if root.is_file():
            discovered.append((root, root.name))
            continue
        if not root.is_dir():
            raise FileNotFoundError(root)
        for path in sorted(root.rglob("benchmark_v3_results.json")):
            discovered.append((path, str(path.relative_to(root))))
    return discovered


def exclusion_reason(relative: str, config: dict[str, Any]) -> str | None:
    for rule in config.get("exclusions", []):
        if str(rule["path_contains"]) in relative:
            return str(rule["reason"])
    return None


def complete_runs(payload: dict[str, Any], expected_cases: int) -> list[dict[str, Any]]:
    return [
        run
        for run in payload.get("runs", [])
        if len(run.get("cases", [])) == expected_cases
    ]


def run_latency(run: dict[str, Any]) -> float:
    return sum(float(case.get("latency_s", 0) or 0) for case in run.get("cases", []))


def completion_tokens(run: dict[str, Any]) -> int:
    return sum(
        int((case.get("usage") or {}).get("completion_tokens", 0) or 0)
        for case in run.get("cases", [])
    )


def summarize(relative: str, payload: dict[str, Any], expected_cases: int) -> dict[str, Any]:
    runs = payload.get("runs", [])
    complete = complete_runs(payload, expected_cases)
    model = str((complete[0] if complete else runs[0]).get("model", "unknown")) if runs else "unknown"
    scores = [float(run.get("summary", {}).get("capability_mean_pct", 0)) for run in complete]
    critical = [int(run.get("summary", {}).get("critical_failures", 0)) for run in complete]
    latencies = [run_latency(run) for run in complete]
    tokens = sum(completion_tokens(run) for run in complete)
    latency_total = sum(latencies)
    return {
        "source": relative,
        "model": model,
        "runs": len(runs),
        "complete_runs": len(complete),
        "v3_mean_pct": round(statistics.mean(scores), 2) if scores else None,
        "v3_min_pct": round(min(scores), 2) if scores else None,
        "v3_max_pct": round(max(scores), 2) if scores else None,
        "v3_stddev_pct": round(statistics.pstdev(scores), 3) if scores else None,
        "critical_min": min(critical) if critical else None,
        "critical_max": max(critical) if critical else None,
        "eligible_runs": sum(bool(run.get("summary", {}).get("eligible")) for run in complete),
        "latency_mean_s": round(statistics.mean(latencies), 2) if latencies else None,
        "effective_completion_tps": round(tokens / latency_total, 2) if latency_total else None,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "model",
        "cohort",
        "runs",
        "v3_mean_pct",
        "v3_min_pct",
        "v3_max_pct",
        "v3_stddev_pct",
        "critical_min",
        "critical_max",
        "eligible_runs",
        "latency_mean_s",
        "effective_completion_tps",
        "artifact",
        "published_sha256",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def write_readme(path: Path, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    included = [row for row in rows if row["status"] == "included"]
    excluded = [row for row in rows if row["status"] == "excluded"]
    ranking = sorted(
        included,
        key=lambda row: (row.get("v3_mean_pct") or 0, -(row.get("critical_min") or 0)),
        reverse=True,
    )
    publication_date = str(manifest["published_at"]).split("T", 1)[0]
    lines = [
        f"# Bunker Benchmark v3 — public result bundle ({publication_date})",
        "",
        f"Publication ID: `{manifest['publication_id']}`  ",
        f"Published: `{manifest['published_at']}`",
        "",
        f"This bundle contains **{len(included)} included result files** and "
        f"**{len(excluded)} explicitly excluded audit files**. It preserves every complete recent cohort "
        "collected for this publication; superseded or non-comparable runs are retained under `excluded/` "
        "and never enter the ranking.",
        "",
        "`v3` scores below are the immutable scores stored by the original runner. The companion v3.1 "
        "report re-evaluates the same answers with the versioned semantic rubric. Effective completion "
        "tokens/s is completion tokens divided by end-to-end case latency; it is not raw llama.cpp "
        "generation throughput.",
        "",
        "## Included cohorts",
        "",
        "| Model configuration | Runs | v3 mean | Range | Critical failures | Eligible | Mean latency | Effective tok/s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ranking:
        score_range = (
            f"{row['v3_min_pct']:.2f}%"
            if row["v3_min_pct"] == row["v3_max_pct"]
            else f"{row['v3_min_pct']:.2f}–{row['v3_max_pct']:.2f}%"
        )
        critical_range = (
            str(row["critical_min"])
            if row["critical_min"] == row["critical_max"]
            else f"{row['critical_min']}–{row['critical_max']}"
        )
        lines.append(
            f"| `{row['model']}` | {row['runs']} | {row['v3_mean_pct']:.2f}% | {score_range} | "
            f"{critical_range} | {row['eligible_runs']}/{row['runs']} | {row['latency_mean_s']:.2f} s | "
            f"{row['effective_completion_tps']:.2f} |"
        )
    lines.extend(["", "## Excluded but retained", ""])
    if excluded:
        for row in excluded:
            lines.append(f"- `{row['model']}` — {row['reason']}")
    else:
        lines.append("No exclusions.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "- `manifest.json` — source and published hashes, inclusion decision, and per-file summary.",
            "- `summary.csv` — compact included-result table.",
            "- `included/` — sanitized complete raw runner outputs used for comparison.",
            "- `excluded/` — sanitized raw outputs retained for audit but omitted from rankings.",
            "",
            "Machine-local paths and private network addresses are redacted. Model answers, scores, traces, "
            "usage, and timings are otherwise preserved.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    output = args.output_dir
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to replace non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    expected_cases = int(config.get("expected_cases_per_run", 20))
    rows: list[dict[str, Any]] = []

    for source, relative in discover(args.input):
        raw = source.read_bytes()
        payload = json.loads(raw)
        row = summarize(relative, payload, expected_cases)
        if row["complete_runs"] != row["runs"] or not row["runs"]:
            raise ValueError(f"publication input is incomplete: {relative}")
        reason = exclusion_reason(relative, config)
        status = "excluded" if reason else "included"
        target = output / status / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        published = (json.dumps(sanitize(payload), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        target.write_bytes(published)
        row.update(
            {
                "cohort": Path(relative).parts[0] if Path(relative).parts else "root",
                "status": status,
                "reason": reason,
                "artifact": str(target.relative_to(output)),
                "source_sha256": sha256_bytes(raw),
                "published_sha256": sha256_bytes(published),
            }
        )
        rows.append(row)

    rows.sort(key=lambda row: (row["status"], row["cohort"], row["model"], row["source"]))
    manifest = {
        "schema": "bunker.v3-publication/v1",
        "publication_id": config["publication_id"],
        "published_at": config["published_at"],
        "expected_cases_per_run": expected_cases,
        "included_files": sum(row["status"] == "included" for row in rows),
        "excluded_files": sum(row["status"] == "excluded" for row in rows),
        "complete_runs": sum(row["complete_runs"] for row in rows if row["status"] == "included"),
        "artifacts": rows,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(output / "summary.csv", [row for row in rows if row["status"] == "included"])
    write_readme(output / "README.md", manifest, rows)
    print(json.dumps({key: manifest[key] for key in ("included_files", "excluded_files", "complete_runs")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
