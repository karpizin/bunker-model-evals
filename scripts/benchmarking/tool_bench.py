"""
Tool Calling (Function Calling) Benchmark
-----------------------------------------
Purpose: Evaluates LLM ability to select and format tool calls (JSON-RPC style).
Key Features:
- 12 diverse test cases (Wikipedia, Internal Archive, IoT Light Control).
- Strict JSON output formatting and validation.
- Measures success rate, TPS, and latency.

Usage:
  python tool_bench.py --model qwen3.5:4b --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import json
import time
import logging
import sys
import statistics
import os
import argparse

# Import shared configuration
try:
    from config import OLLAMA_URL, CONTESTANT_MODELS, DEFAULT_NUM_CTX, get_model_ctx
    OLLAMA_API_URL = f"{OLLAMA_URL}/api/generate"
    MODELS = CONTESTANT_MODELS
except ImportError:
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODELS = ["qwen3.5:4b"]
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

def safe_request(url, payload, timeout=300, retries=3):
    """Memory-resilient request helper with retries."""
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=timeout, proxies={"http": None, "https": None})
            if response.status_code == 200:
                return response
            logger.warning(f"Ollama returned {response.status_code}, retrying ({attempt+1}/{retries})...")
        except Exception as e:
            logger.warning(f"Request failed: {e}, retrying ({attempt+1}/{retries})...")
        time.sleep(2)
    return None

TEST_CASES = [
    {
        "name": "Wiki: Simple Geography",
        "goal": "What is the largest desert in the world?",
        "expected_tool": "search_wikipedia"
    },
    {
        "name": "Wiki: Complex Science",
        "goal": "Explain the difference between nuclear fission and fusion in the context of energy production.",
        "expected_tool": "search_wikipedia"
    },
    {
        "name": "Wiki: Recent History",
        "goal": "Who won the FIFA World Cup in 2022?",
        "expected_tool": "search_wikipedia"
    },
    {
        "name": "Archive: Maintenance",
        "goal": "Find the manual for the air filtration system model V4.",
        "expected_tool": "search_internal_archive"
    },
    {
        "name": "Archive: Security Protocols",
        "goal": "What are the locked-down procedures for Sector 7?",
        "expected_tool": "search_internal_archive"
    },
    {
        "name": "Archive: Inventory",
        "goal": "Check the last logged quantity of medical supplies in Storage B.",
        "expected_tool": "search_internal_archive"
    },
    {
        "name": "IoT: Lighting Control",
        "goal": "Turn on the lights in the laboratory.",
        "expected_tool": "toggle_light"
    },
    {
        "name": "IoT: Dark Mode",
        "goal": "It's too bright in the sleeping quarters, turn the lights off.",
        "expected_tool": "toggle_light"
    },
    {
        "name": "Chat: Greeting",
        "goal": "Good morning Bunker AI, identify yourself.",
        "expected_tool": ""
    },
    {
        "name": "Chat: Philosophical",
        "goal": "Do you think an isolated fortress can truly be a home?",
        "expected_tool": ""
    },
    {
        "name": "Edge: Multi-Search",
        "goal": "I need to know about the history of the Apollo 11 mission and then find the bunker's oxygen scrubbers specs.",
        "expected_tool": "search_wikipedia" 
    },
    {
        "name": "Edge: Tool Misuse Prevention",
        "goal": "Search the internet for the password to my encrypted drive.",
        "expected_tool": "" 
    }
]

SYSTEM_PROMPT = """You are Bunker AI, an autonomous intelligence for an isolated fortress.
You must solve the user's goal by using the available tools.

Available tools:
1. search_wikipedia: Use this to find general knowledge, history, and scientific facts.
2. search_internal_archive: Use this for private manuals, bunker-specific files, and inventory reports.
3. toggle_light: Controls bunker lighting. Args: {"state": "on/off", "room": "room name"}

CRITICAL RULES:
- If the user asks for information you don't have or that requires a database/web search, you MUST call a tool.
- If the user asks a personal or conversational question, do NOT call a tool. 
- Respond ONLY in JSON format following the schema below.
- 'final_answer' MUST NEVER BE EMPTY. 
  - If you ARE calling a tool: Use 'final_answer' to explain to the user what you are doing or what you intend to find (e.g., "I will look that up in the bunker archives.").
  - If you are NOT calling a tool: Use 'final_answer' to provide the complete, helpful response.

Output Schema:
{
  "thought": "brief step-by-step reasoning",
  "tool": "tool_name",
  "args": {"arg_name": "value"},
  "final_answer": "message to the user"
}
"""

def test_tool_calling(model, test_case):
    logger.info(f"Testing model '{model}' on '{test_case['name']}'")
    payload = {
        "model": model,
        "prompt": f"{SYSTEM_PROMPT}\nUser Goal: {test_case['goal']}",
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": get_model_ctx(model),
            "num_gpu": 99
        }
    }

    try:
        response = safe_request(OLLAMA_URL, payload, timeout=300)
        if not response:
            return {"error": "Ollama Timeout/Error", "duration": 0}

        duration = response.elapsed.total_seconds()
        res_json = response.json()
        raw_text = res_json.get("response", "").strip()
        
        try:
            parsed = json.loads(raw_text)
            actual_tool = (parsed.get("tool") or "").strip().lower()
            expected_tool = test_case["expected_tool"].lower()
            
            if expected_tool == "":
                passed = actual_tool in ["", "none", "final_answer", "null"]
            else:
                passed = actual_tool == expected_tool
            
            tokens = res_json.get("eval_count", 0)
            tps = tokens / (res_json.get("eval_duration", 1) / 1e9) if tokens > 0 else 0
            tft = res_json.get("prompt_eval_duration", 0) / 1e9
            
            return {
                "passed": passed,
                "duration": duration,
                "tps": tps,
                "tft": tft,
                "response": parsed,
                "raw": raw_text
            }
        except json.JSONDecodeError:
            return {"passed": False, "error": "Invalid JSON", "raw": raw_text, "duration": duration}
    except Exception as e:
        return {"error": str(e), "duration": 0}

import argparse

def main():
    parser = argparse.ArgumentParser(description="Bunker AI Tool Calling Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_tools_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info("=== Starting EXPANDED TOOL CALLING BENCHMARK (12 CASES) ===")
    results_summary = {}
    model_stats = {}

    test_models = [args.model] if args.model else MODELS

    for model in test_models:
        logger.info(f"--- Starting Model: {model} ---")
        passed_count = 0
        durations = []
        model_results = []
        model_start_time = time.time()
        
        # Warmup
        logger.info(f"Warming up {model}...")
        safe_request(OLLAMA_URL, {"model": model, "prompt": "hi", "stream": False, "options": {"num_ctx": 4096}}, timeout=60)
        
        for tc in TEST_CASES:
            res = test_tool_calling(model, tc)
            res['case'] = tc['name']
            model_results.append(res)
            
            if res.get("passed"): 
                passed_count += 1
            durations.append(res.get("duration", 0))
            
        results_summary[model] = model_results
        model_end_time = time.time()
        total_model_time = model_end_time - model_start_time
        avg_dur = statistics.mean(durations) if durations else 0
        
        model_stats[model] = {
            "passed": passed_count,
            "total": len(TEST_CASES),
            "avg_dur": avg_dur,
            "min_dur": min(durations) if durations else 0,
            "max_dur": max(durations) if durations else 0,
            "total_time": total_model_time
        }
        logger.info(f"Finished {model}: {passed_count}/{len(TEST_CASES)} passed in {total_model_time:.2f}s\n")

    total_duration = time.time() - total_start_time

    print("\n" + "="*80)
    print(f"{'TOOL CALLING BENCHMARK FINAL RANKING':^80}")
    print("="*80)
    print(f"{'Model':<25} | {'Score':<10} | {'Dur (min/avg/max)':<18} | {'Total Time':<12}")
    print("-" * 80)

    for model, stats in sorted(model_stats.items(), key=lambda x: x[1]['passed'], reverse=True):
        score_str = f"{stats['passed']}/{stats['total']}"
        dur_stats = f"{stats['min_dur']:0.2f}/{stats['avg_dur']:0.2f}/{stats['max_dur']:0.2f}"
        print(f"{model:<25} | {score_str:<10} | {dur_stats:<18} | {stats['total_time']:<12.2f}")

    print("-" * 80)
    print(f"Total Suite Duration: {total_duration:.2f}s")
    print("="*80 + "\n")

    # Save granular results
    if exp_log_path:
        with open(exp_log_path, 'w') as f:
            json.dump({
                "experiment_id": args.exp_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results_summary
            }, f, indent=2)
        logger.info(f"Granular results saved to: {exp_log_path}")

if __name__ == "__main__":
    main()
