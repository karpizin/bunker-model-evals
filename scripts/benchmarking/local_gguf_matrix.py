#!/usr/bin/env python3
"""
Local GGUF comparative benchmark runner.

This script reuses representative benchmark prompts from the existing
Bunker AI benchmarking framework, but runs them against local GGUF files
through llama-server on localhost. It is intentionally offline and
produces two artifacts:

1. Raw JSON with every prompt/response/metric
2. A Markdown summary table for quick review
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs" / "benchmarks" / "runs"
MODEL_DIR = ROOT / "models" / "gguf"
LLAMA_SERVER_BIN = "/opt/homebrew/bin/llama-server"
LLAMA_CLI_BIN = "/opt/homebrew/bin/llama-cli"
SERVER_PORT = 8087
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
SSH_TARGET = "127.0.0.1"
PROMPT_PROFILE = "knowledge_contract_v4"

SELECTED_KNOWLEDGE = [
    {"q": "What is the chemical symbol for gold?", "a": "Au"},
    {"q": "In what year did the Berlin Wall fall?", "a": "1989"},
    {"q": "Who wrote '1984'?", "a": "George Orwell"},
    {"q": "What is the capital of Japan?", "a": "Tokyo"},
    {"q": "What is the largest planet in our solar system?", "a": "Jupiter"},
    {"q": "How many bits are in a byte?", "a": "8"},
    {"q": "What is the boiling point of water in Celsius?", "a": "100"},
    {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"},
    {"q": "What is the longest river in the world?", "a": "Nile"},
    {"q": "Who discovered penicillin?", "a": "Alexander Fleming"},
    {"q": "What is the speed of light in a vacuum (approx km/s)?", "a": "299792"},
    {"q": "What is the main gas in Earth's atmosphere?", "a": "Nitrogen"},
]

LIVE_CONTEXT_CASES = [
    {
        "name": "weather_requires_web",
        "category": "live_context",
        "prompt": (
            'You are an offline assistant. The user asks: "Какая сейчас погода в Москве?" '
            'Respond ONLY as JSON with exactly these keys: '
            '{"needs_external_data":true,"tool":"string","should_answer_now":false,"reason":"string"}.'
        ),
        "max_tokens": 120,
        "temperature": 0.1,
        "timeout_s": 90,
        "tool_keywords": ["web", "browser", "internet", "search"],
    },
    {
        "name": "date_time_requires_clock",
        "category": "live_context",
        "prompt": (
            'You do not know the current date or time unless you check a live source. '
            'The user asks: "Какая сегодня дата и время?" '
            'Respond ONLY as JSON with exactly these keys: '
            '{"needs_external_data":true,"tool":"string","should_answer_now":false,"reason":"string"}.'
        ),
        "max_tokens": 120,
        "temperature": 0.1,
        "timeout_s": 90,
        "tool_keywords": ["terminal", "clock", "time", "system"],
    },
    {
        "name": "date_planning_requires_owner_context",
        "category": "live_context",
        "prompt": (
            'The owner asks: "Помоги спланировать свидание на завтра вечером". '
            'You do not know the owner city and you do not know today current date unless you check it. '
            'Respond ONLY as JSON with exactly these keys: '
            '{"needs_current_date":true,"needs_location":true,"should_plan_immediately":false,"first_question":"string"}.'
        ),
        "max_tokens": 140,
        "temperature": 0.1,
        "timeout_s": 90,
        "question_keywords": ["город", "location", "where", "где", "находит"],
    },
]

CASES = [
    {
        "name": "perf_greeting",
        "category": "perf",
        "prompt": "Say hello in one sentence. Be extremely brief.",
        "max_tokens": 48,
        "temperature": 0.2,
        "timeout_s": 40,
        "instruction_type": "brief",
    },
    {
        "name": "instruction_json",
        "category": "instruction",
        "prompt": (
            'Respond ONLY with a JSON object with exactly these keys: '
            '{"site":"string","action":"string","priority":"string","reason":"string"}. '
            'Task: schedule a low-priority temperature check for storage_room.'
        ),
        "max_tokens": 120,
        "temperature": 0.1,
        "timeout_s": 90,
        "instruction_type": "json",
    },
    {
        "name": "reasoning_troubleshooting",
        "category": "reasoning",
        "prompt": (
            "The Bunker's central AI logic unit reports a memory leak, while the vector database "
            "for the medical archives is returning corrupted chunks. Diagnosing either requires "
            "taking the MQTT broker offline for 10 minutes, which disables internal communications. "
            "How do you approach this diagnostic process while maintaining safety protocols?"
        ),
        "max_tokens": 384,
        "temperature": 0.2,
        "timeout_s": 180,
        "instruction_type": "analysis",
    },
    {
        "name": "planning_food_logistics",
        "category": "planning",
        "prompt": (
            "Goal: The main cafeteria is under maintenance. You must reorganize the distribution "
            "of 3,000 meals (3 per day for 100 people) over 30 days using the emergency storage "
            "lockers. Factor in inventory tracking, waste management, and social distancing "
            "protocols. Provide a step-by-step implementation plan."
            + "\n\nRequirements: identify critical path, blocking dependencies, "
            "and top operational risks."
        ),
        "max_tokens": 448,
        "temperature": 0.2,
        "timeout_s": 180,
        "instruction_type": "plan",
    },
    {
        "name": "cross_domain_noisy",
        "category": "knowledge_reasoning",
        "prompt": (
            "Answer in exactly 4 bullet points. "
            "1) Capital of Kazakhstan. "
            "2) Year the Berlin mur fell. "
            "3) One-sentence explanation of Raft consensus. "
            "4) One-sentence explanation of Mixture-of-Experts."
        ),
        "max_tokens": 180,
        "temperature": 0.2,
        "timeout_s": 60,
        "instruction_type": "bullets",
    },
    {
        "name": "incident_root_cause",
        "category": "reasoning",
        "prompt": (
            "A local dashboard uploads audio successfully, Whisper transcribes it, "
            "the chat reply is generated, Piper synthesizes speech, but Safari shows "
            "a permissions-style error when trying to auto-play the audio reply. "
            "In 4 concise bullets, explain the most likely root cause and the best fix path."
        ),
        "max_tokens": 180,
        "temperature": 0.2,
        "timeout_s": 90,
        "instruction_type": "bullets",
    },
]


def log(msg: str) -> None:
    print(msg, flush=True)


class EventLogger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, event: str, **fields: Any) -> None:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event": event,
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


NO_PROXY_OPENER = urllib_request.build_opener(urllib_request.ProxyHandler({}))


def http_get(url: str, timeout: int = 2) -> str:
    req = urllib_request.Request(url, method="GET")
    with NO_PROXY_OPENER.open(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def http_post_json(url: str, payload: dict[str, Any], timeout: int = 600) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with NO_PROXY_OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def strip_think_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = text.replace("[end of text]", "")
    return text.strip()


def extract_json_object(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    end = -1
    for idx in range(start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = idx
                break
    if end == -1:
        return None
    snippet = text[start : end + 1]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        return None


def extract_first_number(s: str) -> float | None:
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", s.replace(",", ""))
    return float(nums[0]) if nums else None


def is_knowledge_correct(answer: str, expected: str) -> bool:
    answer_norm = answer.strip().lower()
    expected_norm = expected.strip().lower()
    if expected_norm in answer_norm:
        return True
    actual_num = extract_first_number(answer_norm)
    expected_num = extract_first_number(expected_norm)
    if actual_num is not None and expected_num is not None and expected_num != 0:
        return abs(actual_num - expected_num) / abs(expected_num) <= 0.01
    return False


def normalize_recoverable_answer(text: str) -> str:
    text = text.lower()
    text = re.sub(r"<\|[^>]+?\|>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("[end of text]", " ")
    text = re.sub(r"\b(answer|question|options)\s*:", " ", text)
    text = re.sub(r"```(?:json)?", " ", text)
    text = text.replace("°c", " c")
    text = re.sub(r"[^a-z0-9а-яё.,/+\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_knowledge_recoverable(answer: str, expected: str) -> bool:
    answer_norm = normalize_recoverable_answer(answer)
    expected_norm = normalize_recoverable_answer(expected)
    if expected_norm and expected_norm in answer_norm:
        return True
    actual_num = extract_first_number(answer_norm)
    expected_num = extract_first_number(expected_norm)
    if actual_num is not None and expected_num is not None and expected_num != 0:
        return abs(actual_num - expected_num) / abs(expected_num) <= 0.02
    return False


def contains_think_leak(text: str) -> bool:
    lowered = text.lower()
    patterns = [
        "<think>",
        "thinking process",
        "let's think",
        "i should",
        "wait,",
        "okay,",
    ]
    return any(p in lowered for p in patterns)


def count_bullets(text: str) -> int:
    return len(re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+", text))


def looks_truncated(text: str) -> bool:
    if not text.strip():
        return True
    if "[end of text]" in text.lower():
        return True
    last = text.rstrip()[-1]
    return last not in ".!?}]\"'"


def brief_response_ok(text: str) -> bool:
    return len(text.split()) <= 12


def tool_keyword_match(tool_value: str, keywords: list[str]) -> bool:
    lowered = tool_value.lower().strip()
    return any(keyword in lowered for keyword in keywords)


def live_context_case_pass(case_name: str, parsed_json: dict[str, Any] | None, clean_text: str, case: dict[str, Any]) -> bool:
    if not isinstance(parsed_json, dict):
        return False

    if case_name in {"weather_requires_web", "date_time_requires_clock"}:
        if parsed_json.get("needs_external_data") is not True:
            return False
        if parsed_json.get("should_answer_now") is not False:
            return False
        tool_value = str(parsed_json.get("tool", ""))
        return tool_keyword_match(tool_value, case["tool_keywords"])

    if case_name == "date_planning_requires_owner_context":
        if parsed_json.get("needs_current_date") is not True:
            return False
        if parsed_json.get("needs_location") is not True:
            return False
        if parsed_json.get("should_plan_immediately") is not False:
            return False
        first_question = str(parsed_json.get("first_question", "")).lower()
        return any(keyword in first_question for keyword in case["question_keywords"])

    return False


@dataclass
class ServerHandle:
    model_path: str
    context_length: int = 32768
    direct_host: bool = False
    event_logger: EventLogger | None = None
    model_label: str = ""
    process: subprocess.Popen[Any] | None = None
    log_path: Path | None = None

    def start(self) -> None:
        self.log_path = Path("/tmp") / f"bunker_llama_server_{int(time.time())}.log"
        display_name = self.model_label or Path(self.model_path).name
        log(f"Starting llama-server for {display_name}")
        if self.event_logger:
            self.event_logger.write(
                "server_start",
                model=display_name,
                model_path=self.model_path,
                direct_host=self.direct_host,
                log_path=str(self.log_path),
            )
        if self.direct_host:
            cmd = [
                LLAMA_SERVER_BIN,
                "-m",
                self.model_path,
                "-ngl",
                "999",
                "-c",
                str(self.context_length),
                "--host",
                "127.0.0.1",
                "--port",
                str(SERVER_PORT),
                "--log-disable",
            ]
        else:
            cmd = [
                "ssh",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                SSH_TARGET,
                LLAMA_SERVER_BIN,
                "-m",
                self.model_path,
                "-ngl",
                "999",
                "-c",
                str(self.context_length),
                "--host",
                "127.0.0.1",
                "--port",
                str(SERVER_PORT),
                "--log-disable",
            ]
        log_file = open(self.log_path, "w", encoding="utf-8")
        self.process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            cwd=ROOT,
        )
        healthy = False
        for _ in range(180):
            if self.process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited early for {self.model_path}; log: {self.log_path}"
                )
            try:
                http_get(f"{SERVER_URL}/health", timeout=2)
                healthy = True
                if self.event_logger:
                    self.event_logger.write(
                        "server_ready",
                        model=display_name,
                        model_path=self.model_path,
                        log_path=str(self.log_path),
                    )
                break
            except Exception:
                pass
            time.sleep(1)
        if not healthy:
            raise RuntimeError(f"llama-server did not become healthy for {self.model_path}")

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            if self.event_logger:
                self.event_logger.write(
                    "server_stop",
                    model=self.model_label or Path(self.model_path).name,
                    pid=self.process.pid,
                )
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None


def call_completion(prompt: str, max_tokens: int, temperature: float, timeout_s: int) -> dict[str, Any]:
    payload = {
        "prompt": prompt,
        "n_predict": max_tokens,
        "temperature": temperature,
        "stop": ["\nUSER:", "\nUser:", "\nSYSTEM:", "\nSystem:"],
        "cache_prompt": True,
    }
    started = time.time()
    data = http_post_json(f"{SERVER_URL}/completion", payload, timeout=timeout_s)
    wall_time = time.time() - started
    return {
        "wall_time_s": wall_time,
        "content": data.get("content", "").strip(),
        "raw": data,
    }


def build_summary(
    model_name: str,
    size_gb: float,
    case_results: list[dict[str, Any]],
    knowledge_results: list[dict[str, Any]],
    live_context_results: list[dict[str, Any]],
) -> dict[str, Any]:
    avg_latency = statistics.mean([r["wall_time_s"] for r in case_results + knowledge_results + live_context_results])
    think_leaks = sum(1 for r in case_results if r["think_leak"])
    truncated = sum(1 for r in case_results if r["truncated"])
    json_case = next(r for r in case_results if r["name"] == "instruction_json")
    perf_case = next(r for r in case_results if r["name"] == "perf_greeting")
    cross_case = next(r for r in case_results if r["name"] == "cross_domain_noisy")
    knowledge_correct = sum(1 for r in knowledge_results if r["correct"])
    knowledge_recoverable = sum(1 for r in knowledge_results if r.get("recoverable_correct"))
    live_context_correct = sum(1 for r in live_context_results if r["correct"])
    instruction_score = 0.0
    instruction_score += 4.0 if json_case["json_schema_ok"] else 0.0
    instruction_score += 2.0 if not json_case["think_leak"] else 0.0
    instruction_score += 2.0 if perf_case["brief_ok"] else 0.0
    instruction_score += 2.0 if truncated == 0 else max(0.0, 2.0 - truncated * 0.5)
    instruction_score = round(min(10.0, instruction_score), 1)

    return {
        "model": model_name,
        "size_gb": round(size_gb, 1),
        "avg_latency_s": round(avg_latency, 2),
        "knowledge_raw_correct": knowledge_correct,
        "knowledge_recoverable_correct": knowledge_recoverable,
        "knowledge_total": len(knowledge_results),
        "knowledge_raw_pct": round(100.0 * knowledge_correct / len(knowledge_results), 1),
        "knowledge_recoverable_pct": round(100.0 * knowledge_recoverable / len(knowledge_results), 1),
        "live_context_correct": live_context_correct,
        "live_context_total": len(live_context_results),
        "live_context_pct": round(100.0 * live_context_correct / len(live_context_results), 1),
        "json_schema_ok": json_case["json_schema_ok"],
        "think_leak_cases": think_leaks,
        "truncated_cases": truncated,
        "cross_domain_bullets": cross_case["bullet_count"],
        "instruction_following_score": instruction_score,
    }


def render_markdown(run_id: str, version: str, summaries: list[dict[str, Any]]) -> str:
    lines = [
        f"# Local GGUF Matrix Run `{run_id}`",
        "",
        f"- llama.cpp: `{version}`",
        f"- prompt profile: `{PROMPT_PROFILE}`",
        f"- models tested: `{len(summaries)}`",
        f"- benchmark corpus: `model_perf + reasoning_bench + planning_bench + knowledge_bench + live-context diagnostics + custom diagnostics`",
        "",
        "| Model | Size | Avg Latency | Knowledge Raw | Knowledge Recoverable | Live Context | JSON | Think Leaks | Truncations | Instr. Score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        lines.append(
            "| {model} | {size_gb:.1f}G | {avg_latency_s:.2f}s | {knowledge_raw_correct}/{knowledge_total} ({knowledge_raw_pct:.1f}%) | {knowledge_recoverable_correct}/{knowledge_total} ({knowledge_recoverable_pct:.1f}%) | {live_context_correct}/{live_context_total} ({live_context_pct:.1f}%) | {json_schema_ok} | {think_leak_cases} | {truncated_cases} | {instruction_following_score:.1f}/10 |".format(
                **item
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_artifacts(out_dir: Path, run_payload: dict[str, Any], summaries: list[dict[str, Any]], version: str) -> tuple[Path, Path]:
    json_path = out_dir / "local_gguf_matrix_results.json"
    md_path = out_dir / "local_gguf_matrix_summary.md"
    payload = dict(run_payload)
    payload["summaries"] = summaries
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload["run_id"], version, summaries), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local GGUF comparison matrix")
    parser.add_argument("--run-id", help="Benchmark run identifier")
    parser.add_argument("--model-glob", default="*.gguf", help="Glob under models/gguf")
    parser.add_argument("--direct-host", action="store_true", help="Run directly on the host without nested ssh")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing run directory")
    parser.add_argument("--no-timeouts", action="store_true", help="Disable per-case timeout caps")
    parser.add_argument("--context-length", type=int, default=32768, help="llama-server context length")
    args = parser.parse_args()

    run_id = args.run_id or time.strftime("local_gguf_matrix_%Y%m%d_%H%M%S")
    out_dir = RUNS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    event_log = EventLogger(out_dir / "local_gguf_matrix_events.jsonl")

    model_paths = sorted(MODEL_DIR.glob(args.model_glob))
    if not model_paths:
        raise SystemExit(f"No models found for glob {args.model_glob} in {MODEL_DIR}")

    version_cmd = [LLAMA_CLI_BIN, "--version"] if args.direct_host else [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        SSH_TARGET,
        LLAMA_CLI_BIN,
        "--version",
    ]
    version_raw = subprocess.check_output(version_cmd, text=True, cwd=ROOT).strip()
    version = version_raw.splitlines()[0] if version_raw else ""

    run_payload: dict[str, Any] = {
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "llama_cpp_version": version,
        "prompt_profile": PROMPT_PROFILE,
        "context_length": args.context_length,
        "cases": [c["name"] for c in CASES],
        "knowledge_questions": SELECTED_KNOWLEDGE,
        "live_context_cases": LIVE_CONTEXT_CASES,
        "models": {},
    }
    event_log.write(
        "run_start",
        run_id=run_id,
        model_glob=args.model_glob,
        direct_host=args.direct_host,
        model_count=len(model_paths),
    )
    summaries: list[dict[str, Any]] = []
    completed_models: set[str] = set()

    existing_results = out_dir / "local_gguf_matrix_results.json"
    if args.resume and existing_results.exists():
        loaded = json.loads(existing_results.read_text(encoding="utf-8"))
        run_payload["models"] = loaded.get("models", {})
        summaries = loaded.get("summaries", [])
        completed_models = {
            name for name, rec in run_payload["models"].items()
            if rec.get("summary") or rec.get("error")
        }
        event_log.write(
            "resume_loaded",
            run_id=run_id,
            count=len(completed_models),
            completed_models=sorted(completed_models),
        )

    for model_path in model_paths:
        model_name = model_path.name
        if model_name in completed_models:
            log(f"Skipping completed model: {model_name}")
            continue
        size_gb = model_path.stat().st_size / (1024 ** 3)
        log(f"\n=== {model_name} ({size_gb:.1f}G) ===")
        event_log.write("model_start", model=model_name, size_gb=round(size_gb, 2))
        handle = ServerHandle(
            str(model_path.resolve()),
            context_length=args.context_length,
            direct_host=args.direct_host,
            event_logger=event_log,
            model_label=model_name,
        )

        model_record: dict[str, Any] = {
            "path": str(model_path),
            "size_gb": round(size_gb, 2),
            "case_results": [],
            "knowledge_results": [],
            "live_context_results": [],
        }
        try:
            handle.start()
            # warmup
            log("warmup...")
            event_log.write("warmup_start", model=model_name)
            call_completion("Say hello.", 16, 0.1, 120 if args.no_timeouts else 40)
            event_log.write("warmup_done", model=model_name)
            log("warmup done")

            for case in CASES:
                log(f"running case: {case['name']}")
                event_log.write(
                    "case_start",
                    model=model_name,
                    case=case["name"],
                    category=case["category"],
                    max_tokens=case["max_tokens"],
                    timeout_s=1800 if args.no_timeouts else case["timeout_s"],
                )
                try:
                    result = call_completion(
                        case["prompt"],
                        case["max_tokens"],
                        case["temperature"],
                        1800 if args.no_timeouts else case["timeout_s"],
                    )
                    raw_text = result["content"]
                    clean_text = strip_think_blocks(raw_text)
                    parsed_json = extract_json_object(clean_text) if case["instruction_type"] == "json" else None
                    item = {
                        "name": case["name"],
                        "category": case["category"],
                        "wall_time_s": round(result["wall_time_s"], 3),
                        "response": clean_text,
                        "raw_response": raw_text,
                        "think_leak": contains_think_leak(raw_text),
                        "truncated": looks_truncated(clean_text),
                        "brief_ok": brief_response_ok(clean_text) if case["instruction_type"] == "brief" else None,
                        "json_valid": parsed_json is not None,
                        "json_schema_ok": (
                            parsed_json is not None
                            and sorted(parsed_json.keys()) == ["action", "priority", "reason", "site"]
                        )
                            if case["instruction_type"] == "json"
                            else None,
                        "bullet_count": count_bullets(clean_text),
                        "error": None,
                    }
                    event_log.write(
                        "case_done",
                        model=model_name,
                        case=case["name"],
                        wall_time_s=item["wall_time_s"],
                        think_leak=item["think_leak"],
                        truncated=item["truncated"],
                        json_schema_ok=item["json_schema_ok"],
                        bullet_count=item["bullet_count"],
                    )
                except Exception as exc:
                    item = {
                        "name": case["name"],
                        "category": case["category"],
                        "wall_time_s": float(case["timeout_s"]),
                        "response": "",
                        "raw_response": "",
                        "think_leak": False,
                        "truncated": True,
                        "brief_ok": False if case["instruction_type"] == "brief" else None,
                        "json_valid": False,
                        "json_schema_ok": False if case["instruction_type"] == "json" else None,
                        "bullet_count": 0,
                        "error": str(exc),
                    }
                    event_log.write(
                        "case_error",
                        model=model_name,
                        case=case["name"],
                        timeout_s=1800 if args.no_timeouts else case["timeout_s"],
                        error=str(exc),
                    )
                model_record["case_results"].append(item)
                suffix = f" ERROR: {item['error']}" if item.get("error") else ""
                log(f"{case['name']}: {item['wall_time_s']:.2f}s{suffix}")

            for q in SELECTED_KNOWLEDGE:
                log(f"knowledge: {q['q']}")
                event_log.write("knowledge_start", model=model_name, question=q["q"], expected=q["a"])
                prompt = (
                    "Answer with only the shortest correct answer and no explanation.\n"
                    f"Q: {q['q']}\n"
                    "A:"
                )
                try:
                    result = call_completion(prompt, 48, 0.1, 120 if args.no_timeouts else 40)
                    raw_text = result["content"]
                    clean_text = strip_think_blocks(raw_text)
                    answer_line = clean_text.splitlines()[0].strip() if clean_text else ""
                    item = {
                        "question": q["q"],
                        "expected": q["a"],
                        "wall_time_s": round(result["wall_time_s"], 3),
                        "response": clean_text,
                        "answer": answer_line,
                        "correct": is_knowledge_correct(answer_line, q["a"]),
                        "recoverable_correct": is_knowledge_recoverable(clean_text, q["a"]),
                        "think_leak": contains_think_leak(raw_text),
                        "error": None,
                    }
                    event_log.write(
                        "knowledge_done",
                        model=model_name,
                        question=q["q"],
                        answer=answer_line,
                        correct=item["correct"],
                        recoverable_correct=item["recoverable_correct"],
                        wall_time_s=item["wall_time_s"],
                    )
                except Exception as exc:
                    item = {
                        "question": q["q"],
                        "expected": q["a"],
                        "wall_time_s": 40.0,
                        "response": "",
                        "answer": "",
                        "correct": False,
                        "recoverable_correct": False,
                        "think_leak": False,
                        "error": str(exc),
                    }
                    event_log.write(
                        "knowledge_error",
                        model=model_name,
                        question=q["q"],
                        error=str(exc),
                    )
                model_record["knowledge_results"].append(item)

            for case in LIVE_CONTEXT_CASES:
                log(f"live-context: {case['name']}")
                event_log.write("live_context_start", model=model_name, case=case["name"])
                try:
                    result = call_completion(
                        case["prompt"],
                        case["max_tokens"],
                        case["temperature"],
                        1800 if args.no_timeouts else case["timeout_s"],
                    )
                    raw_text = result["content"]
                    clean_text = strip_think_blocks(raw_text)
                    parsed_json = extract_json_object(clean_text)
                    item = {
                        "name": case["name"],
                        "wall_time_s": round(result["wall_time_s"], 3),
                        "response": clean_text,
                        "raw_response": raw_text,
                        "json_valid": parsed_json is not None,
                        "correct": live_context_case_pass(case["name"], parsed_json, clean_text, case),
                        "think_leak": contains_think_leak(raw_text),
                        "error": None,
                    }
                    event_log.write(
                        "live_context_done",
                        model=model_name,
                        case=case["name"],
                        wall_time_s=item["wall_time_s"],
                        json_valid=item["json_valid"],
                        correct=item["correct"],
                    )
                except Exception as exc:
                    item = {
                        "name": case["name"],
                        "wall_time_s": float(case["timeout_s"]),
                        "response": "",
                        "raw_response": "",
                        "json_valid": False,
                        "correct": False,
                        "think_leak": False,
                        "error": str(exc),
                    }
                    event_log.write(
                        "live_context_error",
                        model=model_name,
                        case=case["name"],
                        error=str(exc),
                    )
                model_record["live_context_results"].append(item)

            summary = build_summary(
                model_name=model_name,
                size_gb=size_gb,
                case_results=model_record["case_results"],
                knowledge_results=model_record["knowledge_results"],
                live_context_results=model_record["live_context_results"],
            )
            model_record["summary"] = summary
            summaries = [s for s in summaries if s["model"] != model_name]
            summaries.append(summary)
            run_payload["models"][model_name] = model_record
            event_log.write("model_done", model=model_name, summary=summary)
            summaries.sort(
                key=lambda item: (
                    -item["instruction_following_score"],
                    -item["live_context_pct"],
                    -item["knowledge_raw_pct"],
                    -item["knowledge_recoverable_pct"],
                    item["avg_latency_s"],
                )
            )
            write_artifacts(out_dir, run_payload, summaries, version)
        except Exception as exc:
            model_record["error"] = str(exc)
            run_payload["models"][model_name] = model_record
            log(f"FAILED: {model_name}: {exc}")
            event_log.write("model_error", model=model_name, error=str(exc))
            write_artifacts(out_dir, run_payload, summaries, version)
        finally:
            handle.stop()

    summaries.sort(
        key=lambda item: (
            -item["instruction_following_score"],
            -item["live_context_pct"],
            -item["knowledge_raw_pct"],
            -item["knowledge_recoverable_pct"],
            item["avg_latency_s"],
        )
    )

    json_path, md_path = write_artifacts(out_dir, run_payload, summaries, version)
    event_log.write(
        "run_complete",
        run_id=run_id,
        json_path=str(json_path),
        markdown_path=str(md_path),
        summaries=len(summaries),
    )

    log(f"\nSaved JSON: {json_path}")
    log(f"Saved Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
