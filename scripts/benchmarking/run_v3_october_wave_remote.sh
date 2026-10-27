#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}
BUNKER_DATA_ROOT=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
BUNKER_RELEASE_MEDIA_ROOT=${BUNKER_RELEASE_MEDIA_ROOT:-"$HOME/releases/media"}

OUTPUT_ROOT=${OUTPUT_ROOT:-${BUNKER_DATA_ROOT}/benchmarks/bunker-v3-october-wave-20261026}
RUN_TAG=${RUN_TAG:-20261026-fd8f845}
PORT=${PORT:-18081}
WAIT_SECONDS=${WAIT_SECONDS:-30}
MAX_WAIT_SECONDS=${MAX_WAIT_SECONDS:-28800}

RUNNER="$BENCH_ROOT/scripts/benchmarking/run_v3_medium_large_remote.sh"
STATUS_FILE="$OUTPUT_ROOT/october_wave_status.tsv"

mkdir -p "$OUTPUT_ROOT/logs"
touch "$STATUS_FILE"

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
  'Spark-X2.6-4B-Q5_K_M' \
  "${BUNKER_DATA_ROOT}/models/spark-x2.6-4b/Spark-X2.6-4B-Q5_K_M.gguf" \
  '3164766848'

printf '%s\twave\tbenchmark_start\tqwen-main-27b+35b\n' "$(date -Is)" >> "$STATUS_FILE"

OUTPUT_ROOT="$OUTPUT_ROOT" \
RUN_TAG="$RUN_TAG" \
MODEL_FILTER='^(Qwen3.6-27B-Q4_K_M-MTP|Qwen3.6-27B-Q4_K_M|Qwen3.6-27B-UD-IQ3_XXS-MTP|Qwen3.6-27B-UD-IQ2_M|Qwen3.8-27B-UD-Q6_K_M-MTP|Qwen3.6-35B-A3B-UD-Q4_K_M|Qwen3.6-35B-A3B-UD-Q5_K_M-MTP|Qwen3.6-35B-A3B-UD-Q6_K-MTP)$' \
PORT="$PORT" \
bash "$RUNNER"

printf '%s\twave\tbenchmark_finished\tqwen-main-27b+35b\n' "$(date -Is)" >> "$STATUS_FILE"

printf '%s\twave\tbenchmark_start\tqwen-experimental-35b\n' "$(date -Is)" >> "$STATUS_FILE"

OUTPUT_ROOT="$OUTPUT_ROOT" \
RUN_TAG="$RUN_TAG" \
MODEL_FILTER='^(Huihui-Qwen3.6-35B-A3B-abliterated-Q4_K-MTP|Qwen3.6-35B-A3B-Uncensored-Q3_K_P)$' \
PORT="$PORT" \
bash "$RUNNER"

printf '%s\twave\tbenchmark_finished\tqwen-experimental-35b\n' "$(date -Is)" >> "$STATUS_FILE"

wait_for_model \
  'Flint-Q4_K_M' \
  "${BUNKER_DATA_ROOT}/models/flint/Flint-Q4_K_M.gguf" \
  '23387911136'
wait_for_model \
  'Nanbeige4.3-33B-Q4_K_M' \
  "${BUNKER_DATA_ROOT}/models/nanbeige4.3-33b/Nanbeige_Nanbeige4.3-33B-Q4_K_M.gguf" \
  '20788825216'

printf '%s\twave\tbenchmark_start\tflint+nanbeige\n' "$(date -Is)" >> "$STATUS_FILE"

OUTPUT_ROOT="$OUTPUT_ROOT" \
RUN_TAG="$RUN_TAG" \
MODEL_FILTER='^(Flint-Q4_K_M|Nanbeige4.3-33B-Q4_K_M)$' \
PORT="$PORT" \
bash "$RUNNER"

printf '%s\twave\tbenchmark_finished\tflint+nanbeige\n' "$(date -Is)" >> "$STATUS_FILE"
