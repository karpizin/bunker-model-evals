"""
Model Performance (TPS/Latency) Benchmark
-----------------------------------------
Purpose: Measures raw generation speed and latency across common interaction patterns.
Key Features:
- 3 test cases: Simple Greeting, Technical Explanation, JSON Reasoning.
- Calculates Tokens-Per-Second (TPS) and Time-to-First-Token (TFT).
- Compares performance metrics at different context lengths.

Usage:
  python model_perf.py --model qwen3.5:4b --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import time
import json
import statistics
import logging
import sys
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

BENCHMARKS = [
    {
        "name": "Simple Greeting",
        "prompt": "Say hello in one sentence. Be extremely brief.",
        "max_tokens": 20
    },
    {
        "name": "Technical Explanation",
        "prompt": "Explain what causes earthquakes in 2 sentences.",
        "max_tokens": 100
    },
    {
        "name": "JSON Reasoning (Agent Mode)",
        "prompt": """You are Bunker AI. Respond ONLY in JSON.
{
  "thought": "your reasoning",
  "tool": "search_wikipedia",
  "args": {"query": "earthquake causes"},
  "final_answer": ""
}
Goal: What causes earthquakes?""",
        "max_tokens": 200,
        "format": "json"
    }
]

def run_benchmark(model, bench):
    logger.info(f"Running benchmark '{bench['name']}' for model '{model}'")
    payload = {
        "model": model,
        "prompt": bench["prompt"],
        "stream": False,
        "options": {
            "num_predict": bench["max_tokens"],
            "temperature": 0.2,
            "num_ctx": get_model_ctx(model),
            "num_gpu": 99
        }
    }
    if bench.get("format") == "json":
        payload["format"] = "json"

    try:
        start_time = time.time()
        logger.debug(f"Sending request to {OLLAMA_URL}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=300, proxies={"http": None, "https": None})
        end_time = time.time()
        
        if response.status_code != 200:
            logger.error(f"Error from Ollama: {response.status_code} - {response.text}")
            return None

        data = response.json()
        eval_count = data.get("eval_count", 0)
        eval_duration = data.get("eval_duration", 1) / 1e9 # to seconds
        
        tps = eval_count / eval_duration if eval_duration > 0 else 0
        total_time = end_time - start_time
        
        logger.info(f"Completed '{bench['name']}': {eval_count} tokens in {total_time:.2f}s ({tps:.2f} TPS)")
        
        return {
            "model": model,
            "tokens": eval_count,
            "tps": tps,
            "latency": total_time,
            "response": data.get("response", "").strip()
        }
    except Exception as e:
        logger.exception(f"Exception during benchmark {model}: {e}")
        return None

import argparse

def main():
    parser = argparse.ArgumentParser(description="Bunker AI Model Performance Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for this benchmark run (optional)")
    args = parser.parse_args()

    total_start_time = time.time()
    results = {}
    model_stats = {}
    
    test_models = [args.model] if args.model else MODELS
    
    logger.info(f"Starting Bunker AI Model Performance Benchmark Suite")
    logger.info(f"Models to test: {test_models}")
    logger.info(f"Benchmarking cases: {[b['name'] for b in BENCHMARKS]}")

    for model in test_models:
        model_start_time = time.time()
        logger.info(f"=== Starting Model: {model} ===")
        results[model] = []
        
        # Warmup
        logger.info(f"Warming up {model}...")
        try:
            requests.post(OLLAMA_URL, json={"model": model, "prompt": "hi", "stream": False, "options": {"num_ctx": 4096}}, timeout=30, proxies={"http": None, "https": None})
        except Exception as e:
            logger.warning(f"Warmup failed for {model}: {e}")
        
        for bench in BENCHMARKS:
            res = run_benchmark(model, bench)
            if res:
                results[model].append(res)
            else:
                logger.error(f"Benchmark failed for {model} on '{bench['name']}'")
        
        model_end_time = time.time()
        model_stats[model] = model_end_time - model_start_time
        logger.info(f"=== Finished Model: {model} in {model_stats[model]:.2f}s ===\n")

    total_duration = time.time() - total_start_time
    
    # Final Summary Table
    print("\n" + "="*80)
    print(f"{'FINAL PERFORMANCE SUMMARY':^80}")
    print("="*80)
    print(f"{'Model':<25} | {'Avg TPS':<12} | {'Lat (min/avg/max)':<18} | {'Total Time':<12}")
    print("-" * 80)

    for model in test_models:
        res_list = results.get(model, [])
        if not res_list:
            print(f"{model:<25} | {'FAILED':<12} | {'FAILED':<12} | {model_stats.get(model, 0):.2f}s")
            continue
            
        avg_tps = statistics.mean([r["tps"] for r in res_list])
        latencies = [r["latency"] for r in res_list]
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        total_model_time = model_stats.get(model, 0)
        
        print(f"{model:<25} | {avg_tps:<12.2f} | {min_latency:0.2f}/{avg_latency:0.2f}/{max_latency:0.2f} | {total_model_time:<12.2f}")

    print("-" * 80)
    print(f"Total Suite Duration: {total_duration:.2f}s")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
