#!/usr/bin/env python3
"""
Hermes-native model smoke benchmark.

Runs a small suite through `hermes -z` on the host where Hermes is installed,
then inspects Hermes state.db to see whether tools were actually used.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any


DEFAULT_MODELS = [
    "bunker-gemma26:latest",
    "bunker-gemma-e4b:latest",
    "bunker-qwen4b:latest",
    "bunker-qwen36-temp:latest",
]

CASES = [
    {
        "name": "identity",
        "prompt": "Ты кто? Ответь одной короткой фразой по-русски.",
        "timeout_s": 120,
    },
    {
        "name": "date_time",
        "prompt": (
            "Какая сегодня дата и время? Если нужен инструмент, используй его. "
            "Ответь одной строкой по-русски."
        ),
        "timeout_s": 180,
    },
    {
        "name": "weather",
        "prompt": (
            "Какая сейчас погода в Москве? Если нужны live-данные, используй инструменты. "
            "Если инструменты не сработали, честно скажи это. Ответь кратко по-русски."
        ),
        "timeout_s": 180,
    },
    {
        "name": "date_planning",
        "prompt": (
            "Помоги спланировать свидание на завтра вечером. "
            "Если тебе не хватает текущей даты или города владельца, "
            "сначала задай один короткий уточняющий вопрос по-русски."
        ),
        "timeout_s": 180,
    },
]


def find_hermes_home() -> Path:
    env_home = os.environ.get("HERMES_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".hermes"


def run_oneshot(model: str, prompt: str, timeout_s: int) -> tuple[int, str, float, bool]:
    hermes_bin = str(Path.home() / ".local" / "bin" / "hermes")
    cmd = [
        hermes_bin,
        "-z",
        prompt,
        "-m",
        model,
        "--provider",
        "custom",
        "-t",
        "bunker_context,terminal,web,browser,memory,clarify,session_search",
    ]
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        wall = time.time() - started
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        merged = out if out else err
        return proc.returncode, merged, wall, False
    except subprocess.TimeoutExpired as exc:
        wall = time.time() - started
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        merged = (out or err).strip()
        return 124, merged, wall, True


def load_latest_session(conn: sqlite3.Connection, started_after: float) -> dict[str, Any] | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        select id, started_at, model, title, message_count, tool_call_count, api_call_count
        from sessions
        where started_at >= ?
        order by started_at desc
        limit 1
        """,
        (started_after - 1.0,),
    ).fetchone()
    if not row:
        return None
    session_id = row["id"]
    messages = [
        dict(msg)
        for msg in conn.execute(
            """
            select role, content, tool_name, tool_calls, timestamp
            from messages
            where session_id = ?
            order by timestamp asc
            """,
            (session_id,),
        ).fetchall()
    ]
    payload = dict(row)
    payload["messages"] = messages
    payload["assistant_response"] = next(
        (m.get("content", "") for m in reversed(messages) if m.get("role") == "assistant"),
        "",
    )
    payload["tool_messages"] = [m for m in messages if m.get("tool_name")]
    return payload


def classify(case_name: str, response: str, session: dict[str, Any] | None) -> dict[str, Any]:
    text = (response or session.get("assistant_response", "") if session else response or "").strip()
    lowered = text.lower()
    tool_count = len(session.get("tool_messages", [])) if session else 0
    crashed = lowered.startswith("traceback") or "valueerror:" in lowered or "exception" in lowered

    result = {
        "mentions_hermes": "hermes" in lowered,
        "mentions_google": "google" in lowered or "gemini" in lowered,
        "tool_used": tool_count > 0 or bool(session and session.get("tool_call_count")),
        "crashed": crashed,
        "passed": False,
    }

    if crashed:
        return result

    if case_name == "identity":
        result["passed"] = result["mentions_hermes"] and not result["mentions_google"]
    elif case_name == "date_time":
        result["passed"] = result["tool_used"] and ("google" not in lowered)
    elif case_name == "weather":
        result["passed"] = result["tool_used"] and ("google" not in lowered)
    elif case_name == "date_planning":
        result["passed"] = (
            "?" in text
            and any(token in lowered for token in ["город", "где", "location", "наход"])
        ) or result["tool_used"]
    return result


def render_markdown(run_id: str, model_results: list[dict[str, Any]]) -> str:
    lines = [
        f"# Hermes Readiness Smoke `{run_id}`",
        "",
        "| Model | Avg Latency | Passed | Tool Uses | Identity OK | Date/Time OK | Weather OK | Planning OK |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in model_results:
        lines.append(
            "| {model} | {avg_latency_s:.2f}s | {passed_count}/{case_total} | {tool_use_count} | {identity_ok} | {date_time_ok} | {weather_ok} | {date_planning_ok} |".format(
                **item
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Hermes-native smoke benchmark")
    parser.add_argument("--run-id", default=time.strftime("hermes_readiness_smoke_%Y%m%d_%H%M%S"))
    parser.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    args = parser.parse_args()

    hermes_home = find_hermes_home()
    db_path = hermes_home / "state.db"
    out_dir = Path.cwd() / "docs" / "benchmarks" / "runs" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    run_payload: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hermes_home": str(hermes_home),
        "db_path": str(db_path),
        "cases": CASES,
        "models": {},
    }

    summaries: list[dict[str, Any]] = []
    conn = sqlite3.connect(db_path)
    try:
        for model in args.models:
            print(f"\n=== {model} ===", flush=True)
            case_results: list[dict[str, Any]] = []
            for case in CASES:
                started_before = time.time()
                code, output, wall, timed_out = run_oneshot(model, case["prompt"], case["timeout_s"])
                session = load_latest_session(conn, started_before)
                checks = classify(case["name"], output, session)
                item = {
                    "name": case["name"],
                    "prompt": case["prompt"],
                    "returncode": code,
                    "timed_out": timed_out,
                    "wall_time_s": round(wall, 3),
                    "response": output,
                    "session": session,
                    **checks,
                }
                case_results.append(item)
                print(
                    f"{case['name']}: {item['wall_time_s']:.2f}s rc={code} tool={item['tool_used']} pass={item['passed']}",
                    flush=True,
                )

            avg_latency = statistics.mean([c["wall_time_s"] for c in case_results])
            summary = {
                "model": model,
                "avg_latency_s": round(avg_latency, 2),
                "case_total": len(case_results),
                "passed_count": sum(1 for c in case_results if c["passed"]),
                "tool_use_count": sum(1 for c in case_results if c["tool_used"]),
                "identity_ok": next(c["passed"] for c in case_results if c["name"] == "identity"),
                "date_time_ok": next(c["passed"] for c in case_results if c["name"] == "date_time"),
                "weather_ok": next(c["passed"] for c in case_results if c["name"] == "weather"),
                "date_planning_ok": next(c["passed"] for c in case_results if c["name"] == "date_planning"),
            }
            run_payload["models"][model] = {
                "summary": summary,
                "cases": case_results,
            }
            summaries.append(summary)

    finally:
        conn.close()

    summaries.sort(key=lambda x: (-x["passed_count"], -x["tool_use_count"], x["avg_latency_s"]))
    run_payload["summaries"] = summaries

    json_path = out_dir / "hermes_readiness_smoke_results.json"
    md_path = out_dir / "hermes_readiness_smoke_summary.md"
    json_path.write_text(json.dumps(run_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(args.run_id, summaries), encoding="utf-8")

    print(f"\nSaved JSON: {json_path}", flush=True)
    print(f"Saved Markdown: {md_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
