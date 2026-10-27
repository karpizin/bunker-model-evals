#!/bin/bash

# Overnight Benchmark Runner
# Bunker AI Ecosystem - March 2026

LOG_FILE="docs/benchmarks/overnight_results.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"
DATE_STR=$(date '+%Y-%m-%d %H:%M:%S')

echo "====================================================" >> $LOG_FILE
echo "STARTING OVERNIGHT BENCHMARK: $DATE_STR" >> $LOG_FILE
echo "====================================================" >> $LOG_FILE

# 1. Run Standard Direct Orchestrator
echo "[1/3] Running Standard Orchestrator (Direct Approach)..." | tee -a $LOG_FILE
"$PYTHON_BIN" scripts/benchmarking/orchestrator.py >> "$LOG_FILE" 2>&1

# 2. Run Hybrid MCP Benchmark
echo "[2/3] Running Hybrid MCP Benchmark..." | tee -a $LOG_FILE
"$PYTHON_BIN" scripts/benchmarking/mcp_bench_hybrid.py >> "$LOG_FILE" 2>&1

# 3. Run Hybrid Tool Benchmark
echo "[3/3] Running Hybrid Tool Benchmark..." | tee -a $LOG_FILE
"$PYTHON_BIN" scripts/benchmarking/tool_bench_hybrid.py >> "$LOG_FILE" 2>&1

echo "====================================================" >> $LOG_FILE
echo "OVERNIGHT BENCHMARK COMPLETED" >> $LOG_FILE
echo "====================================================" >> $LOG_FILE
