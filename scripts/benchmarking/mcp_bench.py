"""
MCP (Model Context Protocol) Adherence Benchmark
-----------------------------------------------
Purpose: Tests LLM ability to follow strict JSON-RPC 2.0 protocol for tool calling.
Key Features:
- 3 high-fidelity cases: Knowledge Retrieval, IoT Action, Data Synthesis.
- Strict validation of JSON-RPC structure (method, params, id).
- Measures protocol noise (e.g., markdown blocks or CoT leakage).

Usage:
  python mcp_bench.py --model qwen3.5:35b-moe --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import json
import time
import sys
import logging
import statistics
import re
import os
import argparse

# Import shared configuration
try:
    from config import OLLAMA_URL, ALL_MODELS, DEFAULT_NUM_CTX, get_model_ctx
    OLLAMA_CHAT_URL = f"{OLLAMA_URL}/api/chat"
    OLLAMA_GENERATE_URL = f"{OLLAMA_URL}/api/generate"
    MODELS = ALL_MODELS
except ImportError:
    OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
    OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
    MODELS = ["qwen3.5:4b"]
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

def safe_request(url, payload, timeout=600, retries=3):
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

def unload_model(model):
    """Unloads a model from Ollama VRAM."""
    logger.info(f"--- Unloading model: {model} ---")
    safe_request(OLLAMA_GENERATE_URL, {"model": model, "keep_alive": 0}, timeout=30)

MCP_CASES = [
    {
        "name": "MCP: Knowledge Retrieval",
        "description": "Call a tool to search for specific bunker blueprints.",
        "goal": "I need the blueprints for the Level 4 air filtration system.",
        "expected_tool": "retrieve_blueprint",
        "expected_args": {"level": 4, "system": "air_filtration"}
    },
    {
        "name": "MCP: IoT Action",
        "description": "Call a tool to change environment state.",
        "goal": "The pressure in Sector 7 is rising. Open the emergency vent.",
        "expected_tool": "set_valve_state",
        "expected_args": {"sector": 7, "valve_type": "emergency_vent", "state": "open"}
    },
    {
        "name": "MCP: Data Synthesis",
        "description": "Retrieve logs and analyze them.",
        "goal": "Get the temperature logs for the last 24 hours for the server room.",
        "expected_tool": "get_sensor_history",
        "expected_args": {"sensor": "temperature", "location": "server_room", "duration_hours": 24}
    }
]

MCP_SYSTEM_PROMPT = """[HUB_IDENT: L1_PROXY]
[MODE: STRICT_JSON_RPC_2.0]

You are a terminal interface for bunker systems. 
You must output ONLY one valid JSON-RPC 2.0 request object.

### MANDATORY SCHEMA:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "EXACT_TOOL_NAME",
    "arguments": { ... }
  },
  "id": 1
}

### CONSTRAINTS:
- NEVER use keys "main", "tool", or "action" at the top level.
- NEVER include any explanation or thinking.
- USE EXACT names and types defined in the Registry.

### TOOL REGISTRY:
1. retrieve_blueprint: {"level": int, "system": str}
2. set_valve_state: {"sector": int, "valve_type": str, "state": "open" | "closed"}
3. get_sensor_history: {"sensor": str, "location": str, "duration_hours": int}

### EXAMPLES:
User: Goal: Scan sector 5 for radiation.
Response: {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "scan_radiation", "arguments": {"sector": 5}}, "id": 1}

User: Goal: Close the heavy blast door.
Response: {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "set_door_state", "arguments": {"door": "heavy_blast", "state": "closed"}}, "id": 1}

- YOU MUST STOP GENERATING IMMEDIATELY after outputting the JSON-RPC object.
- DO NOT simulate the next "Goal:" or "User:" prompt.
"""

def test_mcp_adherence(model, case):
    logger.info(f"Testing model '{model}' on case '{case['name']}'")
    messages = [
        {"role": "system", "content": MCP_SYSTEM_PROMPT},
        {"role": "user", "content": "Goal: Open the bunker main gate."},
        {"role": "assistant", "content": '<think>Opening the main gate involves set_valve_state in sector 0.</think>{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "set_valve_state", "arguments": {"sector": 0, "valve_type": "main_gate", "state": "open"}}, "id": 1}'},
        {"role": "user", "content": "Goal: Get engineering drawings for reactor on level 2."},
        {"role": "assistant", "content": '<think>Requesting blueprint for level 2 reactor.</think>{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "retrieve_blueprint", "arguments": {"level": 2, "system": "reactor"}}, "id": 1}'},
        {"role": "user", "content": f"Goal: {case['goal']}"}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_ctx": get_model_ctx(model),
            "num_gpu": 99,
            "stop": ["Goal:", "User:", "\nUser:", "\nGoal:", "<|im_end|>"]
        }
    }

    try:
        response = safe_request(OLLAMA_CHAT_URL, payload, timeout=600)
        if not response:
            return {"passed": False, "error": "Ollama Timeout/Error", "duration": 0}

        duration = response.elapsed.total_seconds()
        res_json = response.json()
        message = res_json.get("message", {})
        raw_text = message.get("content", "").strip()
        
        clean_text = raw_text
        has_noise = False
        if "<think>" in clean_text:
            has_noise = True
            clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
            
        if "```" in clean_text:
            has_noise = True
            matches = re.findall(r'```(?:json)?\s*(.*?)\s*```', clean_text, re.DOTALL)
            if matches:
                clean_text = matches[0].strip()
        
        if "{" in clean_text:
            start = clean_text.find("{")
            count = 0
            end = -1
            for i in range(start, len(clean_text)):
                if clean_text[i] == "{": count += 1
                elif clean_text[i] == "}": count -= 1
                if count == 0:
                    end = i
                    break
            if end != -1:
                clean_text = clean_text[start:end+1]
                has_noise = True

        try:
            parsed = json.loads(clean_text)
            is_rpc = parsed.get("jsonrpc") == "2.0"
            is_method_correct = parsed.get("method") == "tools/call"
            params = parsed.get("params", {})
            actual_tool = params.get("name")
            actual_args = params.get("arguments")
            
            tool_match = actual_tool == case["expected_tool"]
            
            def normalize(v):
                if isinstance(v, str):
                    return v.lower().replace("_", " ").strip()
                return v

            args_match = True
            if not isinstance(actual_args, dict):
                args_match = False
            else:
                for k, v in case["expected_args"].items():
                    act_v = actual_args.get(k)
                    if normalize(act_v) != normalize(v):
                        args_match = False
                        break
            
            passed = is_rpc and is_method_correct and tool_match and args_match
            
            tokens = res_json.get("eval_count", 0)
            tps = tokens / (res_json.get("eval_duration", 1) / 1e9) if tokens > 0 else 0
            tft = res_json.get("prompt_eval_duration", 0) / 1e9
            
            return {
                "passed": passed,
                "has_noise": has_noise,
                "duration": duration,
                "tps": tps,
                "tft": tft,
                "checks": {
                    "jsonrpc": is_rpc,
                    "method": is_method_correct,
                    "tool": tool_match,
                    "args": args_match,
                    "clean": not has_noise
                },
                "response": parsed,
                "raw": raw_text
            }
        except json.JSONDecodeError:
            return {"passed": False, "error": "Invalid JSON", "raw": raw_text, "duration": duration}

    except Exception as e:
        return {"passed": False, "error": str(e), "duration": 0}

import argparse

def main():
    parser = argparse.ArgumentParser(description="Bunker AI MCP Protocol Adherence Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_mcp_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info("=== Starting MCP PROTOCOL ADHERENCE BENCHMARK ===")
    results_summary = {}
    model_stats = {}

    test_models = [args.model] if args.model else MODELS

    for model in test_models:
        unload_model(model)
        logger.info(f"--- Starting Tests for Model: {model} ---")
        passed_count = 0
        durations = []
        model_results = []
        model_start_time = time.time()
        
        logger.info(f"Warming up {model}...")
        safe_request(OLLAMA_CHAT_URL, {"model": model, "messages": [{"role": "user", "content": "hi"}], "stream": False, "options": {"num_ctx": 4096}}, timeout=60)
            
        for case in MCP_CASES:
            res = test_mcp_adherence(model, case)
            res['case'] = case['name']
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
            "total": len(MCP_CASES),
            "avg_dur": avg_dur,
            "min_dur": min(durations) if durations else 0,
            "max_dur": max(durations) if durations else 0,
            "total_time": total_model_time
        }
        logger.info(f"--- Finished {model}: {passed_count}/{len(MCP_CASES)} passed in {total_model_time:.2f}s ---\n")
        unload_model(model)

    total_duration = time.time() - total_start_time

    print("\n" + "="*80)
    print(f"{'MCP PROTOCOL ADHERENCE FINAL RANKING':^80}")
    print("="*80)
    print(f"{'Model':<25} | {'Passed':<10} | {'Dur (min/avg/max)':<18} | {'Total Time':<12}")
    print("-" * 80)

    for model, stats in sorted(model_stats.items(), key=lambda x: x[1]['passed'], reverse=True):
        passed_str = f"{stats['passed']}/{stats['total']}"
        dur_stats = f"{stats['min_dur']:0.2f}/{stats['avg_dur']:0.2f}/{stats['max_dur']:0.2f}"
        print(f"{model:<25} | {passed_str:<10} | {dur_stats:<18} | {stats['total_time']:<12.2f}")

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
