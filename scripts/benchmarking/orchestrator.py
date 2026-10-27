"""
Bunker AI Benchmarking Orchestrator
----------------------------------
Purpose: Sequentially executes the entire benchmark suite across multiple LLM models.
Key Features:
- Automates model loading/unloading to manage memory (126GB/128GB RAM context).
- Runs 7 distinct benchmark categories (Perf, Reasoning, Math, Planning, MCP, Knowledge, Tools).
- Centralized experiment logging and directory management.

Usage:
  python orchestrator.py --exp-id run_overnight_01

Dependencies: config.py, requests, child benchmark scripts
"""
import subprocess
import time
import requests
import logging
import argparse
import sys
import os

# Import shared configuration
try:
    from config import OLLAMA_URL, ALL_MODELS
    OLLAMA_API_URL = f"{OLLAMA_URL}/api"
    MODELS = ALL_MODELS
except ImportError:
    OLLAMA_API_URL = "http://localhost:11434/api"
    MODELS = ["qwen3.5:4b"]

BENCHMARK_SCRIPTS = [
    "scripts/benchmarking/model_perf.py",
    "scripts/benchmarking/reasoning_bench.py",
    "scripts/benchmarking/math_bench.py",
    "scripts/benchmarking/planning_bench.py",
    "scripts/benchmarking/mcp_bench.py",
    "scripts/benchmarking/knowledge_bench.py",
    "scripts/benchmarking/tool_bench.py"
]

def load_model(model):
    logger.info(f"--- Loading model: {model} ---")
    try:
        # We use a keep_alive of 5m so it stays in memory for our tests
        response = requests.post(
            f"{OLLAMA_BASE_URL}/generate", 
            json={"model": model, "prompt": "", "keep_alive": "5m"},
            timeout=600,
            proxies={"http": None, "https": None}
        )
        if response.status_code == 200:
            logger.info(f"Successfully loaded {model}")
            return True
        else:
            logger.error(f"Failed to load {model}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error loading model {model}: {e}")
        return False

def unload_model(model):
    logger.info(f"--- Unloading model: {model} ---")
    try:
        # keep_alive: 0 immediately unloads the model
        requests.post(
            f"{OLLAMA_BASE_URL}/generate", 
            json={"model": model, "prompt": "", "keep_alive": 0},
            timeout=30,
            proxies={"http": None, "https": None}
        )
        logger.info(f"Successfully sent unload request for {model}")
    except Exception as e:
        logger.error(f"Error unloading model {model}: {e}")

def run_script(script, model, exp_id=None):
    logger.info(f"Executing {script} for model {model} (Exp: {exp_id})...")
    try:
        cmd = [sys.executable, script, "--model", model]
        if exp_id:
            cmd.extend(["--exp-id", exp_id])
            
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            logger.info(f"Successfully completed {script}")
        else:
            logger.error(f"Script {script} failed with exit code {result.returncode}")
    except Exception as e:
        logger.error(f"Exception running script {script}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bunker AI Benchmarking Orchestrator")
    parser.add_argument("--model", type=str, help="Specify a single model to test")
    parser.add_argument("--exp-id", type=str, help="Specify an experiment ID for this run")
    args = parser.parse_args()

    exp_id = args.exp_id if args.exp_id else time.strftime("%Y%m%d_%H%M%S")
    
    # Create experiment directory
    exp_dir = os.path.join("docs", "benchmarks", "runs", exp_id)
    os.makedirs(exp_dir, exist_ok=True)
    
    total_suite_start = time.time()
    logger.info(f"=== BUNKER AI ORCHESTRATOR: SEQUENTIAL BENCHMARKING (EXP: {exp_id}) ===")
    
    test_models = [args.model] if args.model else MODELS
    
    for model in test_models:
        logger.info(f"\n{'#'*60}")
        logger.info(f"### TESTING MODEL: {model}")
        logger.info(f"{'#'*60}\n")
        
        if load_model(model):
            for script in BENCHMARK_SCRIPTS:
                run_script(script, model, exp_id)
            
            unload_model(model)
        else:
            logger.error(f"Skipping benchmarks for {model} due to load failure.")
            
    total_duration = time.time() - total_suite_start
    logger.info(f"\n=== OVERALL SUITE COMPLETED IN {total_duration/60:.2f} MINUTES ===")

if __name__ == "__main__":
    main()
