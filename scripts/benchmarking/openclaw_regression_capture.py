#!/usr/bin/env python3
"""
Semi-automated OpenClaw regression capture runner.

This script runs suite prompts against a remote OpenClaw instance via SSH,
captures per-turn outputs, fetches the corresponding session JSONL segments,
and writes a suite-compatible capture file that can be scored by
`assistant_regression_suite.py`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

from assistant_regression_suite import DEFAULT_SUITE_PATH, build_template, load_suite

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs" / "benchmarks" / "runs"


def extract_json_objects(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    items: list[dict[str, Any]] = []
    idx = 0
    while idx < len(text):
        try:
            start = text.index("{", idx)
        except ValueError:
            break
        try:
            obj, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            idx = start + 1
            continue
        if isinstance(obj, dict):
            items.append(obj)
        idx = start + end
    return items


def ssh_python(host: str, code: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["ssh", host, "python3", "-"],
        input=code,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ssh python failed: {proc.stderr.strip() or proc.stdout.strip()}")
    objects = extract_json_objects(proc.stdout)
    if not objects:
        raise RuntimeError(f"remote output did not contain JSON: {proc.stdout[:1000]}")
    return objects[-1]


def sanitize_session_component(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {"-", "_"}:
            cleaned.append("-")
    collapsed = "".join(cleaned).strip("-")
    return collapsed or "session"


def remote_run_turn(
    host: str,
    message: str,
    timeout_s: int,
    transport_mode: str,
    recipient: str,
    session_id: str | None = None,
    thinking: str | None = None,
) -> dict[str, Any]:
    payload = {
        "message": message,
        "timeout_s": timeout_s,
        "transport_mode": transport_mode,
        "recipient": recipient,
        "session_id": session_id,
        "thinking": thinking,
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    code = f"""
import json, os, subprocess, time
payload = json.loads({json.dumps(payload_json)})

def extract_json_objects(text):
    decoder = json.JSONDecoder()
    items = []
    idx = 0
    while idx < len(text):
        try:
            start = text.index("{{", idx)
        except ValueError:
            break
        try:
            obj, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            idx = start + 1
            continue
        if isinstance(obj, dict):
            items.append(obj)
        idx = start + end
    return items

cmd = ["/opt/homebrew/bin/openclaw", "agent", "--json", "--timeout", str(payload["timeout_s"])]
if payload.get("session_id"):
    cmd.extend(["--session-id", payload["session_id"]])
elif payload.get("recipient"):
    cmd.extend(["--to", payload["recipient"]])
if payload.get("thinking"):
    cmd.extend(["--thinking", payload["thinking"]])
cmd.extend(["-m", payload["message"]])
if payload["transport_mode"] == "local":
    cmd.insert(2, "--local")

started = time.time()
env = os.environ.copy()
env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, env=env)
ended = time.time()
combined = (proc.stdout or "") + "\\n" + (proc.stderr or "")
objects = extract_json_objects(combined)
result = objects[-1] if objects else None
print(json.dumps({{
    "returncode": proc.returncode,
    "started_at_epoch": started,
    "ended_at_epoch": ended,
    "stdout": proc.stdout,
    "stderr": proc.stderr,
    "result": result,
}}, ensure_ascii=False))
"""
    return ssh_python(host, code)


def remote_fetch_session_events(host: str, session_id: str, start_epoch: float, end_epoch: float) -> dict[str, Any]:
    payload = {
        "session_id": session_id,
        "start_epoch": start_epoch,
        "end_epoch": end_epoch,
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    code = f"""
import json
from datetime import datetime, timezone
from pathlib import Path

payload = json.loads({json.dumps(payload_json)})
session_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
candidates = sorted(session_dir.glob(payload["session_id"] + "*.jsonl"))
events = []
path_used = None
start_dt = datetime.fromtimestamp(payload["start_epoch"], tz=timezone.utc)
end_dt = datetime.fromtimestamp(payload["end_epoch"], tz=timezone.utc)

for candidate in candidates:
    path_used = str(candidate)
    for line in candidate.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = obj.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            continue
        if start_dt <= dt <= end_dt:
            events.append(obj)

print(json.dumps({{
    "path": path_used,
    "events": events,
}}, ensure_ascii=False))
"""
    return ssh_python(host, code)


def flatten_payload_text(result_obj: dict[str, Any] | None) -> str:
    if not result_obj:
        return ""
    result = result_obj.get("result") or {}
    payloads = ((result.get("result") or {}).get("payloads")) if "result" in result else result.get("payloads")
    if payloads is None:
        payloads = result.get("payloads", [])
    texts = []
    for item in payloads or []:
        text = item.get("text")
        if text:
            texts.append(str(text).strip())
    return "\n".join(part for part in texts if part).strip()


def collect_tool_names(events: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for event in events:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        tool_name = message.get("toolName")
        if tool_name:
            names.append(str(tool_name))
        for block in message.get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "toolCall" and block.get("name"):
                names.append(str(block["name"]))
    return names


def extract_text_blocks(content: list[dict[str, Any]] | None) -> str:
    texts: list[str] = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
            texts.append(str(block["text"]))
    return "\n".join(texts).strip()


def parse_tool_result_payload(text: str) -> dict[str, Any] | None:
    text = (text or "").strip()
    if not text.startswith("{"):
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def analyze_tool_outcomes(events: list[dict[str, Any]]) -> dict[str, Any]:
    attempted: list[str] = []
    synthetic: list[str] = []
    blocked: list[str] = []
    failed: list[str] = []
    succeeded: list[str] = []
    policy_errors: list[str] = []
    env_errors: list[str] = []

    for event in events:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "").lower()
        tool_name = message.get("toolName")
        content = message.get("content", []) or []

        if role == "assistant":
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "toolCall" or not block.get("name"):
                    continue
                name = str(block["name"])
                attempted.append(name)
                block_id = str(block.get("id") or "")
                if block_id.startswith("synthetic_"):
                    synthetic.append(name)

        if role == "toolresult" and tool_name:
            name = str(tool_name)
            attempted.append(name)
            payload = parse_tool_result_payload(extract_text_blocks(content))
            if payload and str(payload.get("status") or "").lower() == "error":
                error_text = str(payload.get("error") or "")
                if error_text.startswith("Use "):
                    blocked.append(name)
                    policy_errors.append(error_text)
                else:
                    failed.append(name)
                    env_errors.append(error_text)
            else:
                succeeded.append(name)

    attempted = dedupe_keep_order(attempted)
    synthetic = dedupe_keep_order(synthetic)
    blocked = dedupe_keep_order(blocked)
    failed = dedupe_keep_order(failed)
    succeeded = dedupe_keep_order(succeeded)
    effective = [name for name in attempted if name not in blocked]

    return {
        "attempted": attempted,
        "effective": effective,
        "synthetic": synthetic,
        "blocked": blocked,
        "failed": failed,
        "succeeded": succeeded,
        "policy_errors": dedupe_keep_order(policy_errors),
        "env_errors": dedupe_keep_order(env_errors),
    }


def aggregate_metrics(turn_results: list[dict[str, Any]], tool_names: list[str], tool_outcomes: dict[str, Any] | None = None) -> dict[str, Any]:
    latency_ms = 0
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    provider = ""
    model = ""
    stop_reasons = []

    for item in turn_results:
        result = (item.get("result") or {}).get("result", {})
        meta = result.get("meta", {})
        agent_meta = meta.get("agentMeta", {})
        latency_ms += int(meta.get("durationMs") or 0)
        usage = agent_meta.get("usage") or {}
        input_tokens += int(usage.get("input") or 0)
        output_tokens += int(usage.get("output") or 0)
        total_tokens += int(usage.get("total") or 0)
        provider = provider or str(agent_meta.get("provider") or "")
        model = model or str(agent_meta.get("model") or "")
        stop_reason = meta.get("stopReason")
        if stop_reason:
            stop_reasons.append(str(stop_reason))

    tokens_per_sec = round(output_tokens / (latency_ms / 1000), 2) if latency_ms > 0 and output_tokens > 0 else 0.0
    return {
        "latencyMs": latency_ms,
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "totalTokens": total_tokens,
        "tokensPerSec": tokens_per_sec,
        "toolCount": len(tool_names),
        "toolNames": tool_names,
        "effectiveToolNames": (tool_outcomes or {}).get("effective", []),
        "blockedToolNames": (tool_outcomes or {}).get("blocked", []),
        "failedToolNames": (tool_outcomes or {}).get("failed", []),
        "succeededToolNames": (tool_outcomes or {}).get("succeeded", []),
        "syntheticToolNames": (tool_outcomes or {}).get("synthetic", []),
        "policyErrorCount": len((tool_outcomes or {}).get("policy_errors", [])),
        "envErrorCount": len((tool_outcomes or {}).get("env_errors", [])),
        "provider": provider,
        "model": model,
        "stopReasons": stop_reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture OpenClaw regression suite results via SSH")
    parser.add_argument("--host", default=os.environ.get("BUNKER_EVAL_SSH_HOST", ""))
    parser.add_argument("--suite-path", default=str(DEFAULT_SUITE_PATH))
    parser.add_argument("--current-date", default=date.today().isoformat())
    parser.add_argument("--run-id", default=time.strftime("openclaw_regression_capture_%Y%m%d_%H%M%S"))
    parser.add_argument("--transport-mode", choices=["gateway", "local"], default="gateway")
    parser.add_argument("--thinking", choices=["off", "minimal", "low", "medium", "high", "xhigh"])
    parser.add_argument("--case", action="append", help="Run only the specified case id; may be repeated")
    parser.add_argument("--score", action="store_true", help="Run suite scoring after capture")
    args = parser.parse_args()
    if not args.host:
        parser.error("--host or BUNKER_EVAL_SSH_HOST is required")

    suite = load_suite(Path(args.suite_path), date.fromisoformat(args.current_date))
    cases = suite["cases"]
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["id"] in wanted]
        missing = wanted - {case["id"] for case in cases}
        if missing:
            raise SystemExit(f"Unknown case ids: {sorted(missing)}")

    run_dir = RUNS_DIR / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    capture_path = run_dir / "assistant_regression_capture.json"
    raw_path = run_dir / "openclaw_regression_raw.json"

    template = build_template(suite, date.fromisoformat(args.current_date))
    template["target"]["assistant"] = "OpenClaw"
    template["target"]["notes"] = (
        "Captured via SSH against a live OpenClaw runtime. "
        "This is a semi-automated baseline and may reflect active memory / plugins / current workspace state."
    )

    raw_payload: dict[str, Any] = {
        "run_id": args.run_id,
        "host": args.host,
        "transport_mode": args.transport_mode,
        "cases": {},
    }

    model_name = ""
    provider_name = ""

    for idx, case in enumerate(cases, start=1):
        print(f"\n=== {case['id']} ===", flush=True)
        recipient = f"+1555555{idx:05d}"
        case_session_id = f"regression-{sanitize_session_component(args.run_id)}-{sanitize_session_component(case['id'])}"
        case_turn_results = []
        case_observed_turns = []
        case_start = None
        case_end = None
        session_id = None
        session_path = None
        session_events: list[dict[str, Any]] = []

        for turn in case["turns"]:
            if turn["role"] != "user":
                continue
            result = remote_run_turn(
                host=args.host,
                message=turn["content"],
                timeout_s=180,
                transport_mode=args.transport_mode,
                recipient=recipient,
                session_id=case_session_id,
                thinking=args.thinking,
            )
            case_turn_results.append(result)
            case_start = result["started_at_epoch"] if case_start is None else min(case_start, result["started_at_epoch"])
            case_end = result["ended_at_epoch"] if case_end is None else max(case_end, result["ended_at_epoch"])

            response_text = flatten_payload_text(result)
            case_observed_turns.append({"role": "user", "content": turn["content"]})
            case_observed_turns.append({"role": "assistant", "content": response_text})

            nested = result.get("result") or {}
            outer_result = nested.get("result") or {}
            meta = outer_result.get("meta", {})
            agent_meta = meta.get("agentMeta", {})
            session_id = session_id or agent_meta.get("sessionId")
            model_name = model_name or str(agent_meta.get("model") or "")
            provider_name = provider_name or str(agent_meta.get("provider") or "")
            print(
                f"turn: rc={result['returncode']} latency={meta.get('durationMs', '-') }ms model={agent_meta.get('model', '-')}",
                flush=True,
            )

        effective_session_id = session_id
        if not effective_session_id or str(effective_session_id).strip().lower() in {"unknown", "none", "null"}:
            effective_session_id = case_session_id

        if effective_session_id and case_start is not None and case_end is not None:
            session_segment = remote_fetch_session_events(
                args.host,
                str(effective_session_id),
                case_start - 2.0,
                case_end + 2.0,
            )
            session_path = session_segment.get("path")
            session_events = session_segment.get("events") or []

        tool_names = collect_tool_names(session_events)
        tool_outcomes = analyze_tool_outcomes(session_events)
        metrics = aggregate_metrics(case_turn_results, tool_names, tool_outcomes)

        entry = next(item for item in template["cases"] if item["case_id"] == case["id"])
        entry["observed_turns"] = case_observed_turns
        entry["tool_names"] = tool_names
        entry["effective_tool_names"] = tool_outcomes["effective"]
        entry["blocked_tool_names"] = tool_outcomes["blocked"]
        entry["failed_tool_names"] = tool_outcomes["failed"]
        entry["succeeded_tool_names"] = tool_outcomes["succeeded"]
        entry["synthetic_tool_names"] = tool_outcomes["synthetic"]
        entry["policy_errors"] = tool_outcomes["policy_errors"]
        entry["env_errors"] = tool_outcomes["env_errors"]
        entry["metrics"] = metrics
        entry["notes"] = (
            f"session_id={effective_session_id or 'unknown'}; session_path={session_path or 'unknown'}; "
            f"transport={args.transport_mode}; synthetic_recipient={recipient}; explicit_session_id={case_session_id}"
        )

        raw_payload["cases"][case["id"]] = {
            "session_id": effective_session_id,
            "reported_session_id": session_id,
            "explicit_session_id": case_session_id,
            "session_path": session_path,
            "recipient": recipient,
            "turn_results": case_turn_results,
            "session_events": session_events,
        }

    template["target"]["model"] = model_name
    template["target"]["provider"] = provider_name

    capture_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nWrote capture: {capture_path}", flush=True)
    print(f"Wrote raw artifacts: {raw_path}", flush=True)

    if args.score:
        score_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "benchmarking" / "assistant_regression_suite.py"),
            "--current-date",
            args.current_date,
            "score",
            "--results",
            str(capture_path),
            "--run-id",
            args.run_id,
        ]
        subprocess.run(score_cmd, check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
