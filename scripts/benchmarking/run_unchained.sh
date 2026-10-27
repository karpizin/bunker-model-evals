#!/bin/bash

# Unchained LLM Benchmark Runner
# Bunker AI Ecosystem - March 2026

LOG_FILE="docs/benchmarks/unchained_results.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"
DATE_STR=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure the log directory exists
mkdir -p docs/benchmarks

echo "====================================================" >> $LOG_FILE
echo "STARTING UNCHAINED BENCHMARK: $DATE_STR" >> $LOG_FILE
echo "====================================================" >> $LOG_FILE

# Default model if not provided
MODEL=${1:-"qwen3.5:4b"}

echo "Running Unchained Benchmark for model: $MODEL" | tee -a $LOG_FILE

# Run the python script
"$PYTHON_BIN" scripts/benchmarking/unchained_bench.py --model "$MODEL" >> "$LOG_FILE" 2>&1

echo "====================================================" >> $LOG_FILE
echo "UNCHAINED BENCHMARK COMPLETED" >> $LOG_FILE
echo "====================================================" >> $LOG_FILE

echo "Results saved to $LOG_FILE"
