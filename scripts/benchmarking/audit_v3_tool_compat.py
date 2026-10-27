#!/usr/bin/env python3
"""Audit archived Benchmark v3 results for recoverable tool-call mismatches."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from tool_call_normalizer import canonical_agent_action, normalize_tool_response
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tool_call_normalizer import canonical_agent_action, normalize_tool_response


def protocol_failed(case: dict[str, Any]) -> bool:
    return any(item.get("protocol_error") for item in case.get("trace", []))


def response_is_recoverable(raw: str, index: int) -> tuple[bool, str]:
    normalized = normalize_tool_response(raw)
    action = canonical_agent_action(normalized)
    source = str(normalized.get("source_format", "unknown"))
    if action is None:
        return False, source
    if source == "plain_text" and index == 0:
        return False, source
    return True, source


def audit_result(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    run = payload["runs"][0]
    failed_cases = [case for case in run["cases"] if protocol_failed(case)]
    recoverable = 0
    formats: set[str] = set()
    for case in failed_cases:
        parsed = [response_is_recoverable(raw, index) for index, raw in enumerate(case["raw_responses"])]
        formats.update(source for _, source in parsed)
        if parsed and all(ok for ok, _ in parsed):
            recoverable += 1
    return {
        "model": run["model"],
        "score": run["summary"]["capability_mean_pct"],
        "protocol_failures": len(failed_cases),
        "recoverable": recoverable,
        "unresolved": len(failed_cases) - recoverable,
        "formats": ", ".join(sorted(formats)) or "-",
        "empty_reasoning": sum(
            1
            for case in run["cases"]
            if case.get("reasoning_content_chars", 0) > 0 and not case.get("answer", "").strip()
        ),
        "truncated": run["summary"]["truncated_cases"],
    }


def result_files(paths: list[str]) -> list[Path]:
    found: set[Path] = set()
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if path.is_file():
            found.add(path)
        elif path.is_dir():
            found.update(path.rglob("benchmark_v3_results.json"))
    return sorted(found)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Result JSON files or directories")
    args = parser.parse_args()
    audits = [audit_result(path) for path in result_files(args.paths)]
    audits.sort(key=lambda item: (-item["protocol_failures"], item["score"]))
    print("| Model | Score | Protocol failures | Recoverable | Unresolved | Formats | Empty reasoning | Truncated |")
    print("|---|---:|---:|---:|---:|---|---:|---:|")
    for item in audits:
        print(
            f"| {item['model']} | {item['score']:.2f}% | {item['protocol_failures']} | "
            f"{item['recoverable']} | {item['unresolved']} | {item['formats']} | "
            f"{item['empty_reasoning']} | {item['truncated']} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
