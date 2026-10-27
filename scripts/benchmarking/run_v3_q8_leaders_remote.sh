#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}
BUNKER_DATA_ROOT=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
BUNKER_RELEASE_MEDIA_ROOT=${BUNKER_RELEASE_MEDIA_ROOT:-"$HOME/releases/media"}

OUTPUT_ROOT=${OUTPUT_ROOT:-${BUNKER_DATA_ROOT}/benchmarks/bunker-v3-q8-leaders-20261027}
RUN_TAG=${RUN_TAG:-20261027-q8-v31}
RUNNER=${RUNNER:-$BENCH_ROOT/scripts/benchmarking/run_v3_medium_large_remote.sh}
MODEL_SPECS_FILE=${MODEL_SPECS_FILE:-$BENCH_ROOT/scripts/benchmarking/manifests/bunker_benchmark_v3_q8_leaders.models}
TOTAL_RUNS=${TOTAL_RUNS:-5}
QUEUE_WAIT=${QUEUE_WAIT:-172800}
DOWNLOAD_WAIT=${DOWNLOAD_WAIT:-172800}
PORT=${PORT:-18081}

QWEN_MODEL=${BUNKER_DATA_ROOT}/models/qwen3.8-27b-q8/Qwen3.8-27B-Q8_0.gguf
QWEN_SIZE=29047086048
QWEN_DRAFT=${BUNKER_DATA_ROOT}/models/qwen3.8-27b-unsloth/mtp-Qwen3.8-27B-Q4_0.gguf
QWEN_DRAFT_SIZE=1369590656
E4B_Q6_MODEL=${BUNKER_DATA_ROOT}/models/gemma-4-e4b/gemma-4-E4B-it-Q6_K.gguf
E4B_Q6_SIZE=7074929792
E4B_Q8_MODEL=${BUNKER_DATA_ROOT}/models/gemma-4-e4b/gemma-4-E4B-it-Q8_0.gguf
E4B_Q8_SIZE=8192953472
GEMMA_MODEL=${BUNKER_DATA_ROOT}/models/gemma-4-31b/gemma-4-31B-it-Q8_0.gguf
GEMMA_SIZE=32635677632

mkdir -p "$OUTPUT_ROOT/logs"
STATUS_FILE="$OUTPUT_ROOT/q8_leaders_status.tsv"

wait_for_size() {
  local label=$1
  local path=$2
  local expected=$3
  local deadline=$((SECONDS + DOWNLOAD_WAIT))
  local actual=0

  while (( SECONDS < deadline )); do
    if [[ -f "$path" ]]; then
      actual=$(stat -c %s "$path")
      # aria2 can expose the final logical file size while sparse ranges are
      # still missing.  Starting llama.cpp at that point produces valid-looking
      # loads backed by incomplete tensors and meaningless benchmark output.
      if [[ "$actual" -eq "$expected" && ! -e "$path.aria2" ]]; then
        printf '%s\t%s\tartifact_ready\tsize=%s\n' \
          "$(date -Is)" "$label" "$actual" >> "$STATUS_FILE"
        return 0
      fi
      if [[ "$actual" -gt "$expected" ]]; then
        printf '%s\t%s\tsize_mismatch\texpected=%s actual=%s\n' \
          "$(date -Is)" "$label" "$expected" "$actual" >> "$STATUS_FILE"
        return 1
      fi
    fi
    sleep 30
  done

  printf '%s\t%s\tdownload_timeout\texpected=%s actual=%s aria2_sidecar=%s\n' \
    "$(date -Is)" "$label" "$expected" "$actual" \
    "$([[ -e "$path.aria2" ]] && printf yes || printf no)" >> "$STATUS_FILE"
  return 1
}

wait_for_port_release() {
  local deadline=$((SECONDS + QUEUE_WAIT))

  while curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; do
    if (( SECONDS >= deadline )); then
      printf '%s\tq8-leaders\tqueue_timeout\tport=%s\n' \
        "$(date -Is)" "$PORT" >> "$STATUS_FILE"
      return 1
    fi
    sleep 30
  done
}

run_model() {
  local label=$1

  wait_for_port_release
  printf '%s\t%s\tqueued\truns=%s\n' \
    "$(date -Is)" "$label" "$TOTAL_RUNS" >> "$STATUS_FILE"
  OUTPUT_ROOT="$OUTPUT_ROOT" \
  RUN_TAG="$RUN_TAG" \
  RUNS="$TOTAL_RUNS" \
  MODEL_SPECS_FILE="$MODEL_SPECS_FILE" \
  MODEL_FILTER="^${label}$" \
  QUEUE_WAIT=0 \
  PORT="$PORT" \
  bash "$RUNNER"
}

wait_for_size qwen-q8 "$QWEN_MODEL" "$QWEN_SIZE"
wait_for_size qwen-mtp "$QWEN_DRAFT" "$QWEN_DRAFT_SIZE"
run_model Qwen3.8-27B-Q8_0-MTP

wait_for_size gemma-e4b-q6 "$E4B_Q6_MODEL" "$E4B_Q6_SIZE"
run_model gemma-4-E4B-it-Q6_K

wait_for_size gemma-e4b-q8 "$E4B_Q8_MODEL" "$E4B_Q8_SIZE"
run_model gemma-4-E4B-it-Q8_0

wait_for_size gemma-q8 "$GEMMA_MODEL" "$GEMMA_SIZE"
run_model gemma-4-31B-it-Q8_0

python3 "$BENCH_ROOT/scripts/benchmarking/rescore_bunker_benchmark_v3.py" \
  --input "$OUTPUT_ROOT" \
  --output-json "$OUTPUT_ROOT/bunker_benchmark_v3_1_q8_leaders.json" \
  --output-report "$OUTPUT_ROOT/BUNKER_BENCHMARK_V3_1_Q8_LEADERS.md" \
  > "$OUTPUT_ROOT/logs/v3_1_rescore.log" 2>&1

printf '%s\tq8-leaders\tfinished\truns=%s\n' \
  "$(date -Is)" "$TOTAL_RUNS" >> "$STATUS_FILE"
