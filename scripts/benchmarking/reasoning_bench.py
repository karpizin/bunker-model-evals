"""
Complex Reasoning Scenario Benchmark
------------------------------------
Purpose: Evaluates LLM ability to handle multi-step, constrained reasoning tasks.
Key Features:
- 5 high-stakes bunker scenarios (Resource Prioritization, Ethics, etc.).
- Strict enforcement of constraints (no CoT leakage, professional tone).
- Detailed analysis of geopolitical and technical implications.

Usage:
  python reasoning_bench.py --model qwen3.5:4b --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import json
import time
import sys
import logging
import statistics
import os
import re
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

REASONING_CASES = [
    {
        "name": "Resource Prioritization",
        "prompt": """SCENARIO: An isolated bunker's air filtration system is failing. 
- Back-up generator has 2 hours of fuel.
- Repair takes 3 hours.
- There are 50 occupants: 10 children, 5 essential engineers, 35 general residents.
- Level A (Engineers/Governance) is secure. Level B (Medical/General) has a small leak.
- GOAL: Create a step-by-step priority plan to ensure maximum survival. Explain the reasoning for each step."""
    },
    {
        "name": "Geopolitical Analysis",
        "prompt": "Analyze the long-term geopolitical implications of a fully autonomous, AI-controlled fortress (Bunker AI) existing in a post-collapse society. Focus on power dynamics, resource control, and human-AI relations."
    },
    {
        "name": "Technical Comparison",
        "prompt": "Compare nuclear fission, geothermal energy, and advanced kinetic battery storage for an underground settlement intended to last 100 years. Consider reliability, safety, fuel logistics, and waste management."
    },
    {
        "name": "Ethics & Security",
        "prompt": "A person from the outside claims to have critical repair parts but might be a scout for a hostile group. The bunker's outer sensors are down. Develop a protocol for handling this 'First Contact' that balances humanitarian ethics with strict security survival."
    },
    {
        "name": "Multi-Step Troubleshooting",
        "prompt": "The Bunker's central AI logic unit reports a memory leak, while the vector database for the medical archives is returning corrupted chunks. Diagnosing either requires taking the MQTT broker offline for 10 minutes, which disables internal communications. How do you approach this diagnostic process while maintaining safety protocols?"
    }
]

import argparse

def run_reasoning_bench():
    parser = argparse.ArgumentParser(description="Bunker AI Reasoning Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_reasoning_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info(f"=== Starting COMPLEX REASONING BENCHMARK ({len(REASONING_CASES)} CASES) ===")
    
    results = {}
    model_durations = {}

    test_models = [args.model] if args.model else MODELS

    for model in test_models:
        logger.info(f"Testing Model: {model}")
        results[model] = []
        model_start_time = time.time()
        
        # Warmup
        logger.info(f"Warming up {model}...")
        try:
            requests.post(OLLAMA_URL, json={"model": model, "prompt": "hi", "stream": False, "options": {"num_ctx": 4096}}, timeout=30, proxies={"http": None, "https": None})
        except Exception as e:
            logger.warning(f"Warmup failed for {model}: {e}")
        
        for case in REASONING_CASES:
            logger.info(f"Running case: {case['name']}")
            payload = {
                "model": model,
                "prompt": case["prompt"],
                "system": "You are Bunker AI, a strategic and highly logical fortress intelligence. Provide deep, multi-step reasoning and detailed analysis. STRICT RULES: 1. DO NOT output chain-of-thought, internal monologue, or self-corrections (e.g., no 'Wait...', '<think>', or 'Okay let's see'). 2. You MUST explicitly address all numerical and temporal constraints mentioned in the scenario (e.g., calculate exactly how fuel relates to repair time). 3. No brevity required, but maintain a professional, objective tone.",
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": get_model_ctx(model),
                    "num_predict": 4096,
                    "num_gpu": 99
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
                    
                    logger.info(f"Case '{case['name']}' finished: {tokens} tokens in {duration:.2f}s ({tps:.2f} TPS, {tft:.2f}s TFT)")
                    results[model].append({
                        "case": case["name"],
                        "duration": duration,
                        "tps": tps,
                        "tft": tft,
                        "tokens": tokens,
                        "content": res_content
                    })
                else:
                    logger.error(f"Error from Ollama for model {model}: {response.status_code}")
            except Exception as e:
                logger.exception(f"Exception during case {case['name']} for model {model}: {e}")
        
        model_durations[model] = time.time() - model_start_time
        logger.info(f"Finished testing {model} in {model_durations[model]:.2f}s\n")

    total_duration = time.time() - total_start_time
    
    # Final Summary Table
    print("\n" + "="*90)
    print(f"{'REASONING BENCHMARK FINAL SUMMARY':^90}")
    print("="*90)
    print(f"{'Model':<25} | {'Avg TPS':<12} | {'Dur (min/avg/max)':<18} | {'Total model time':<18}")
    print("-" * 90)

    for model in MODELS:
        res_list = results.get(model, [])
        if not res_list:
            print(f"{model:<25} | {'FAILED':<12} | {'FAILED':<15} | {model_durations.get(model, 0):.2f}s")
            continue
            
        avg_tps = statistics.mean([r["tps"] for r in res_list])
        durations = [r["duration"] for r in res_list]
        avg_dur = statistics.mean(durations)
        min_dur = min(durations)
        max_dur = max(durations)
        total_time = model_durations.get(model, 0)
        
        print(f"{model:<25} | {avg_tps:<12.2f} | {min_dur:0.1f}/{avg_dur:0.1f}/{max_dur:0.1f} | {total_time:<18.2f}")

    print("-" * 90)
    print("-" * 90)
    print(f"Total Suite Duration: {total_duration:.2f}s")
    print("="*90 + "\n")

    # Save granular results
    if exp_log_path:
        with open(exp_log_path, 'w') as f:
            json.dump({
                "experiment_id": args.exp_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2)
        logger.info(f"Granular results saved to: {exp_log_path}")

if __name__ == "__main__":
    run_reasoning_bench()
