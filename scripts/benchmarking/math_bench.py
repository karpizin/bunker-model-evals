"""
Quantitative Reasoning (Math) Benchmark
---------------------------------------
Purpose: Tests LLM ability to solve multi-step mathematical and logic problems.
Key Features:
- 5 diverse case studies (Geometric Scaling, Compound Interest, etc.).
- Forces step-by-step reasoning with "#### Final Result:" marker.
- Measures tokens-per-second (TPS) and time-to-first-token (TFT).

Usage:
  python math_bench.py --model qwen3.5:4b --exp-id run_01

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

MATH_CASES = [
    {
        "name": "Geometric Scaling (Cube)",
        "prompt": "Problem: You have a cube. If you increase the length of each edge by exactly 2 times (double it), by how many times will the total volume of the cube increase? Explain your reasoning step-by-step and provide the final multiplier.",
        "expected_answer": "8"
    },
    {
        "name": "Compound Interest (Basic)",
        "prompt": "Problem: An investment of $1,000 grows at a fixed annual interest rate of 10%, compounded annually. What will be the total value of the investment after exactly 5 years? Show your calculation steps and provide the final amount rounded to the nearest dollar.",
        "expected_answer": "1611"
    },
    {
        "name": "Arithmetic Progression",
        "prompt": "Problem: What is the sum of all integers from 1 to 100 inclusive? Describe the formula or method you use to find the result.",
        "expected_answer": "5050"
    },
    {
        "name": "Logical Ratios (Mixing)",
        "prompt": "Problem: You have two containers. Container A has 2 liters of pure water. Container B has 3 liters of a 10% salt solution. If you mix them together, what is the final concentration of salt in the mixture as a percentage? Show the steps.",
        "expected_answer": "6"
    },
    {
        "name": "Physics: Speed/Time/Distance",
        "prompt": "Problem: A car travels from City A to City B at an average speed of 60 km/h and returns from City B to City A along the same route at an average speed of 40 km/h. What is the average speed for the entire round trip? Hint: It is not 50 km/h. Explain why.",
        "expected_answer": "48"
    }
]

def run_math_bench():
    parser = argparse.ArgumentParser(description="Bunker AI Quantitative Reasoning Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_math_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info(f"=== Starting QUANTITATIVE REASONING (MATH) BENCHMARK ({len(MATH_CASES)} CASES) ===")
    
    results = {}
    
    # In orchestrator mode, args.model is usually provided
    target_model = args.model if args.model else "qwen3.5:4b" # Default to 4b for standalone test
    
    logger.info(f"Testing Model: {target_model}")
    results[target_model] = []
    
    # Warmup
    logger.info(f"Warming up {target_model}...")
    try:
        requests.post(OLLAMA_URL, json={"model": target_model, "prompt": "2+2=", "stream": False}, timeout=30, proxies={"http": None, "https": None})
    except Exception as e:
        logger.warning(f"Warmup failed: {e}")

    for case in MATH_CASES:
        logger.info(f"Running case: {case['name']}")
        payload = {
            "model": target_model,
            "prompt": case["prompt"],
            "system": "You are a mathematical reasoning engine. Solve the problem step-by-step. You MUST provide the final numerical or logical result clearly at the very end of your response, preceded by '#### Final Result:'. Accuracy is paramount.",
            "stream": False,
            "options": {
                "temperature": 0.0, # Zero temp for math
                "num_ctx": get_model_ctx(target_model),
                "num_predict": 1024
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
                    "duration": duration,
                    "tps": tps,
                    "tft": tft,
                    "tokens": tokens,
                    "content": res_content,
                    "expected_hint": case["expected_answer"]
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

    print(f"\nMath Benchmark for {target_model} completed in {total_duration:.2f}s")

if __name__ == "__main__":
    run_math_bench()
