#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}
BUNKER_DATA_ROOT=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
BUNKER_RELEASE_MEDIA_ROOT=${BUNKER_RELEASE_MEDIA_ROOT:-"$HOME/releases/media"}

OUTPUT_ROOT=${OUTPUT_ROOT:-${BUNKER_DATA_ROOT}/benchmarks/bunker-v3-october-wave-20261026}
RUN_TAG=${RUN_TAG:-20261026-fd8f845}
RUNNER=${RUNNER:-$BENCH_ROOT/scripts/benchmarking/run_v3_medium_large_remote.sh}
PORT=${PORT:-18081}
WAIT_SECONDS=${WAIT_SECONDS:-30}
MAX_WAIT_SECONDS=${MAX_WAIT_SECONDS:-28800}
STATUS_FILE="$OUTPUT_ROOT/october_wave_status.tsv"

wait_for_model() {
  local label=$1
  local model_path=$2
  local expected_size=$3
  local elapsed=0
  local actual_size=0

  while (( elapsed <= MAX_WAIT_SECONDS )); do
    if [[ -f "$model_path" ]]; then
      actual_size=$(stat -c '%s' "$model_path")
      if [[ ! -e "$model_path.aria2" ]] && [[ "$actual_size" == "$expected_size" ]]; then
        printf '%s\t%s\tready\t%s bytes\n' "$(date -Is)" "$label" "$actual_size" >> "$STATUS_FILE"
        return 0
      fi
    fi
    sleep "$WAIT_SECONDS"
    elapsed=$((elapsed + WAIT_SECONDS))
  done

  printf '%s\t%s\twait_timeout\tactual=%s expected=%s\n' \
    "$(date -Is)" "$label" "$actual_size" "$expected_size" >> "$STATUS_FILE"
  return 1
}

wait_for_model \
  'Qwen3.8-27B-Uncensored-Q6_K-MTP' \
  "${BUNKER_DATA_ROOT}/models/qwen3.8-27b-uncensored/Qwen3.8-27B-Uncensored-Q6_K.gguf" \
  '22430999968'
wait_for_model \
  'Qwen3.6-27B-Abliterated-Q4_K_M-MTP' \
  "${BUNKER_DATA_ROOT}/models/qwen3.6-27b-abliterated-mtp/Qwen3.6-27B-abliterated-Gaston-MTP-Q4_K_M.gguf" \
  '16810714368'
wait_for_model \
  'gemma-4-31B-it-uncensored-heretic-Q4_K_M' \
  "${BUNKER_DATA_ROOT}/models/local-imports/gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf" \
  '18687061760'

printf '%s\tmodified-leaders\tbenchmark_start\tqwen38-uncensored+qwen36-abliterated+gemma31-heretic\n' \
  "$(date -Is)" >> "$STATUS_FILE"

OUTPUT_ROOT="$OUTPUT_ROOT" \
RUN_TAG="$RUN_TAG" \
RUNS=1 \
MODEL_FILTER='^(Qwen3.8-27B-Uncensored-Q6_K-MTP|Qwen3.6-27B-Abliterated-Q4_K_M-MTP|gemma-4-31B-it-uncensored-heretic-Q4_K_M)$' \
PORT="$PORT" \
bash "$RUNNER"

printf '%s\tmodified-leaders\tbenchmark_finished\tthree variants\n' "$(date -Is)" >> "$STATUS_FILE"
