#!/usr/bin/env python3
"""Run the OpenClaw local model suite against MLX models via mlx_lm.server."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import openclaw_local_model_suite as base


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODELS_DIR = ROOT / "models" / "mlx"
DEFAULT_RUNS_DIR = ROOT / "docs" / "benchmarks" / "runs"
DEFAULT_MLX_SERVER = ROOT / ".venv-mlx" / "bin" / "mlx_lm.server"


@dataclass
class MlxModelSpec:
    name: str
    path: Path
    size_bytes: int


def discover_mlx_models(models_dir: Path) -> list[MlxModelSpec]:
    models: list[MlxModelSpec] = []
    for model_dir in sorted(models_dir.iterdir() if models_dir.exists() else []):
        if not model_dir.is_dir():
            continue
        if not (model_dir / "config.json").exists():
            continue
        safetensors = sorted(model_dir.glob("*.safetensors"))
        if not safetensors:
            continue
        if list(model_dir.rglob("*.incomplete")):
            continue
        size = sum(path.stat().st_size for path in safetensors)
        models.append(MlxModelSpec(name=model_dir.name, path=model_dir.resolve(), size_bytes=size))
    return models


def start_mlx_server(
    mlx_server: Path,
    model: MlxModelSpec,
    port: int,
    log_dir: Path,
    timeout: int,
    max_tokens: int,
    temperature: float,
    extra_args: list[str],
) -> subprocess.Popen[str]:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"mlx-server-{base.safe_name(model.name)}.log"
    cmd = [
        str(mlx_server),
        "--model",
        str(model.path),
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--max-tokens",
        str(max_tokens),
        "--temp",
        str(temperature),
    ]
    cmd.extend(extra_args)
    env = os.environ.copy()
    log_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT, text=True, env=env)
    proc._openclaw_log_file = log_f  # type: ignore[attr-defined]
    deadline = time.time() + timeout
    models_url = f"http://127.0.0.1:{port}/v1/models"
    while time.time() < deadline:
        if proc.poll() is not None:
            log_f.flush()
            raise RuntimeError(f"mlx_lm.server exited early for {model.name}; see {log_path}")
        if base.get_json(models_url, timeout=2) is not None:
            return proc
        time.sleep(1)
    raise TimeoutError(f"mlx_lm.server was not ready for {model.name} within {timeout}s")


def stop_server(proc: subprocess.Popen[str] | None) -> None:
    if not proc:
        return
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    log_f = getattr(proc, "_openclaw_log_file", None)
    if log_f:
        log_f.close()


def chat_completion(
    port: int,
    model_path: Path,
    mode: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> tuple[str, dict[str, Any], float]:
    system = base.OPENCLAW_TOOL_SYSTEM if mode == "tool_json" else base.OPENCLAW_CHAT_SYSTEM
    payload = {
        "model": str(model_path),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    start = time.time()
    data = base.post_json(f"http://127.0.0.1:{port}/v1/chat/completions", payload, timeout=timeout)
    elapsed = time.time() - start
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {}) if isinstance(choice, dict) else {}
    text = message.get("content", "") or ""
    return text.strip(), data, elapsed


def direct_chat_completion(
    model_obj: Any,
    tokenizer: Any,
    mode: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> tuple[str, dict[str, Any], float]:
    from mlx_lm.generate import make_sampler, stream_generate

    system = base.OPENCLAW_TOOL_SYSTEM if mode == "tool_json" else base.OPENCLAW_CHAT_SYSTEM
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        formatted_prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    else:
        formatted_prompt = f"{system}\n\nUser: {prompt}\nAssistant:"
    sampler = make_sampler(temp=temperature)
    start = time.time()
    chunks: list[str] = []
    last_response: Any = None
    for response in stream_generate(
        model_obj,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=max_tokens,
        sampler=sampler,
    ):
        chunks.append(response.text)
        last_response = response
    elapsed = time.time() - start
    usage = {}
    finish_reason = None
    if last_response is not None:
        usage = {
            "prompt_tokens": last_response.prompt_tokens,
            "completion_tokens": last_response.generation_tokens,
            "total_tokens": last_response.prompt_tokens + last_response.generation_tokens,
        }
        finish_reason = last_response.finish_reason
    text = "".join(chunks).strip()
    data = {
        "choices": [{"message": {"content": text}, "finish_reason": finish_reason}],
        "usage": usage,
    }
    return text, data, elapsed


def run_suite(args: argparse.Namespace) -> int:
    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    cases = suite["cases"][: args.limit_cases] if args.limit_cases else suite["cases"]
    if args.case_id:
        wanted = set(args.case_id)
        cases = [case for case in cases if case.get("id") in wanted]
    suite = {**suite, "cases": cases}

    models = discover_mlx_models(Path(args.models_dir))
    if args.only:
        needles = [n.lower() for n in args.only]
        models = [m for m in models if any(n in m.name.lower() or n in str(m.path).lower() for n in needles)]
    if args.max_models:
        models = models[: args.max_models]
    if not models:
        print("No complete MLX models discovered.", file=sys.stderr)
        return 2

    run_id = args.run_id or datetime.now().strftime("openclaw-mlx-model-suite-%Y%m%d-%H%M%S")
    run_dir = Path(args.output_dir) / run_id
    log_dir = run_dir / "server-logs"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run dir: {run_dir}")
    print(f"Models: {len(models)}")
    print(f"Cases: {len(cases)}")
    print("Model order:")
    for model in models:
        print(f"  - {model.name} ({model.size_bytes/1024**3:.2f} GiB)")

    results: list[dict[str, Any]] = []
    for model in models:
        print(f"\n=== MODEL {model.name} ===", flush=True)
        proc: subprocess.Popen[str] | None = None
        direct_model: Any = None
        direct_tokenizer: Any = None
        model_result: dict[str, Any] = {
            "model": f"mlx / {model.name}",
            "path": str(model.path),
            "size_bytes": model.size_bytes,
            "cases": [],
        }
        try:
            if args.backend == "direct":
                from mlx_lm import load

                direct_model, direct_tokenizer = load(str(model.path))
            else:
                proc = start_mlx_server(
                    Path(args.mlx_server),
                    model,
                    args.port,
                    log_dir,
                    args.start_timeout,
                    args.max_tokens,
                    args.temperature,
                    args.server_extra_args,
                )
            time.sleep(args.cooldown_s)
            for idx, case in enumerate(cases, 1):
                print(f"[{idx:02d}/{len(cases)}] {case['id']}", flush=True)
                try:
                    if args.backend == "direct":
                        text, data, latency = direct_chat_completion(
                            direct_model,
                            direct_tokenizer,
                            case.get("mode", "chat"),
                            case["prompt"],
                            args.temperature,
                            args.max_tokens,
                        )
                    else:
                        text, data, latency = chat_completion(
                            args.port,
                            model.path,
                            case.get("mode", "chat"),
                            case["prompt"],
                            args.temperature,
                            args.max_tokens,
                            args.case_timeout,
                        )
                    score = base.score_case(case, text)
                    usage = data.get("usage", {})
                    diagnostics = base.chat_response_metadata(data)
                    model_result["cases"].append(
                        {
                            "id": case["id"],
                            "category": case.get("category"),
                            "mode": case.get("mode"),
                            "latency_s": latency,
                            "score": score["score"],
                            "passed_weight": score["passed_weight"],
                            "total_weight": score["total_weight"],
                            "valid_json": score["valid_json"],
                            "tool": score["tool"],
                            "completion_tokens": usage.get("completion_tokens"),
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "total_tokens": usage.get("total_tokens"),
                            "finish_reason": diagnostics["finish_reason"],
                            "response_chars": diagnostics["response_chars"],
                            "reasoning_content": diagnostics["reasoning_content"],
                            "reasoning_content_chars": diagnostics["reasoning_content_chars"],
                            "content_empty_with_reasoning": diagnostics["content_empty_with_reasoning"],
                            "response": text,
                            "checks": score["checks"],
                        }
                    )
                    print(f"    score={score['score']*100:.1f}% latency={latency:.1f}s", flush=True)
                except Exception as exc:
                    model_result["cases"].append(
                        {
                            "id": case["id"],
                            "category": case.get("category"),
                            "mode": case.get("mode"),
                            "latency_s": 0,
                            "score": 0,
                            "error": str(exc),
                            "response": "",
                            "checks": [],
                        }
                    )
                    print(f"    ERROR {exc}", flush=True)
        except Exception as exc:
            model_result["error"] = str(exc)
            print(f"MODEL ERROR: {exc}", flush=True)
        finally:
            stop_server(proc)
            results.append(model_result)
            base.write_reports(run_dir, suite, results)

    base.write_reports(run_dir, suite, results)
    print(f"\nReport: {run_dir / 'openclaw_local_model_suite_report.md'}")
    print(f"Summary: {run_dir / 'openclaw_local_model_suite_summary.csv'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default=str(base.DEFAULT_SUITE))
    parser.add_argument("--models-dir", default=str(DEFAULT_MODELS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_RUNS_DIR))
    parser.add_argument("--mlx-server", default=str(DEFAULT_MLX_SERVER))
    parser.add_argument("--run-id")
    parser.add_argument("--only", action="append", help="Substring filter; can be repeated")
    parser.add_argument("--max-models", type=int)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--case-id", action="append", help="Run only this case id; can be repeated")
    parser.add_argument("--port", type=int, default=18082)
    parser.add_argument("--start-timeout", type=int, default=240)
    parser.add_argument("--case-timeout", type=int, default=240)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--cooldown-s", type=float, default=1.0)
    parser.add_argument("--server-extra-args", action="append", default=[])
    parser.add_argument("--backend", choices=["server", "direct"], default="server")
    args = parser.parse_args()
    return run_suite(args)


if __name__ == "__main__":
    raise SystemExit(main())
