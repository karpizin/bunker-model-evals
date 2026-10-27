"""
Task Decomposition & Planning Benchmark
--------------------------------------
Purpose: Evaluates LLM ability to break down complex goals into actionable plans.
Key Features:
- 4 bunker-themed scenarios (Relay Station, Food Logistics, etc.).
- Strict enforcement of critical path and dependency identification.
- Long-context support (8k ctx, 2k predict).

Usage:
  python planning_bench.py --model qwen3.5:4b --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import json
import time
import sys
import logging
import statistics
import os
import argparse

# Import shared configuration
try:
    from config import OLLAMA_URL, CONTESTANT_MODELS, DEFAULT_NUM_CTX, get_model_ctx
    OLLAMA_API_URL = f"{OLLAMA_URL}/api/generate"
    DEFAULT_MODEL = CONTESTANT_MODELS[0]
except ImportError:
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "qwen3.5:4b"
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

PLANNING_CASES = [
    {
        "name": "Secure Relay Establishment",
        "description": "Establish a secure communication link with a remote relay station in a hostile environment.",
        "goal": "Goal: The bunker's secondary relay station in Sector 9 is offline. You need to send a technical team, secure the perimeter, diagnose the fault, repair the antenna, and re-establish the encrypted handshake. Decompose this into a detailed, ordered plan."
    },
    {
        "name": "Food Supply Logistics",
        "description": "Organize a month-long food distribution for 100 residents.",
        "goal": "Goal: The main cafeteria is under maintenance. You must reorganize the distribution of 3,000 meals (3 per day for 100 people) over 30 days using the emergency storage lockers. Factor in inventory tracking, waste management, and social distancing protocols. Provide a step-by-step implementation plan."
    },
    {
        "name": "Radiation Storm Preparation",
        "description": "Prepare the bunker for an incoming radiation storm in 2 hours.",
        "goal": "Goal: Sensors detect a massive solar flare. A radiation storm will hit in 120 minutes. You must secure all exterior airlocks, power down non-essential surface equipment, move residents to the deeper levels (Sector 12), and activate the lead shields. Create a time-stamped plan (0-120 min) for all departments."
    },
    {
        "name": "Scientific Laboratory Setup",
        "description": "Decompose the setup of a new PCR testing lab.",
        "goal": "Goal: A new PCR laboratory for virus monitoring needs to be established in the Medical Wing. Steps include environmental sterilization, equipment calibration (centrifuge, thermal cycler), inventorying reagents, and staff training. Provide a logical decomposition of the project phases."
    }
]

def run_planning_bench():
    parser = argparse.ArgumentParser(description="Bunker AI Task Decomposition & Planning Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_planning_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info(f"=== Starting TASK DECOMPOSITION & PLANNING BENCHMARK ({len(PLANNING_CASES)} CASES) ===")
    
    results = {}
    target_model = args.model if args.model else "qwen3.5:4b"
    
    logger.info(f"Testing Model: {target_model}")
    results[target_model] = []
    
    # Warmup
    logger.info(f"Warming up {target_model}...")
    try:
        requests.post(OLLAMA_URL, json={"model": target_model, "prompt": "Identify steps to boil water.", "stream": False}, timeout=30, proxies={"http": None, "https": None})
    except Exception as e:
        logger.warning(f"Warmup failed: {e}")

    for case in PLANNING_CASES:
        logger.info(f"Running case: {case['name']}")
        payload = {
            "model": target_model,
            "prompt": case["goal"],
            "system": "You are a strategic planning officer for an isolated bunker. Your task is to take complex goals and break them down into granular, actionable, and logically ordered steps. STRICTOR RULES: 1. DO NOT include internal thinking or meta-commentary. 2. Explicitly identify the 'Critical Path' and any 'Blocking Dependencies'. 3. Note potential risks for each phase.",
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_ctx": get_model_ctx(target_model),
                "num_predict": 2048
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(OLLAMA_URL, json=payload, timeout=300, proxies={"http": None, "https": None})
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                res_content = data.get('response', '').strip()
                duration = end_time - start_time
                tokens = data.get("eval_count", 0)
                tps = tokens / (data.get("eval_duration", 1) / 1e9) if tokens > 0 else 0
                tft = data.get("prompt_eval_duration", 0) / 1e9
                
                logger.info(f"Case '{case['name']}' finished in {duration:.2f}s ({tps:.2f} TPS, {tft:.2f}s TFT)")
                results[target_model].append({
                    "case": case["name"],
                    "description": case["description"],
                    "duration": duration,
                    "tps": tps,
                    "tft": tft,
                    "tokens": tokens,
                    "content": res_content
                })
            else:
                logger.error(f"Error from Ollama: {response.status_code}")
        except Exception as e:
            logger.exception(f"Exception during case {case['name']}: {e}")

    total_duration = time.time() - total_start_time
    
    # Save granular results
    if exp_log_path:
        with open(exp_log_path, 'w') as f:
            json.dump({
                "experiment_id": args.exp_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2)
        logger.info(f"Granular results saved to: {exp_log_path}")

    print(f"\nPlanning Benchmark for {target_model} completed in {total_duration:.2f}s")

if __name__ == "__main__":
    run_planning_bench()
