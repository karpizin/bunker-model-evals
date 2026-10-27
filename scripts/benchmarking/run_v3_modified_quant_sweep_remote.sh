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
PROXY=${PROXY:-http://127.0.0.1:7890}
MODEL_DIR=${MODEL_DIR:-${BUNKER_DATA_ROOT}/models/quant-sweep-temp}
MIN_FREE_BYTES=${MIN_FREE_BYTES:-21474836480}
KEEP_ARTIFACTS=${KEEP_ARTIFACTS:-1}
STATUS_FILE="$OUTPUT_ROOT/october_wave_status.tsv"

mkdir -p "$MODEL_DIR"

# label|url|filename|exact byte size
MODELS=(
  'Qwen3.6-35B-A3B-Uncensored-Q6_K_P|https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf|Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf|30649317504'
  'Huihui-Qwen3.6-35B-A3B-abliterated-Q6_K-MTP|https://huggingface.co/huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF/resolve/main/Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q6_K.gguf|Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q6_K.gguf|29207678176'
  'Qwen3.6-35B-A3B-Uncensored-Q8_K_P|https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf|Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf|43605014656'
  'Huihui-Qwen3.6-35B-A3B-abliterated-Q8_0-MTP|https://huggingface.co/huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF/resolve/main/Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q8_0.gguf|Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q8_0.gguf|37801096416'
)

result_complete() {
  local result_path=$1
  [[ -f "$result_path" ]] && python3 - "$result_path" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)
complete = sum(1 for run in payload.get("runs", []) if len(run.get("cases", [])) == 20)
raise SystemExit(0 if complete >= 1 else 1)
PY
}

for spec in "${MODELS[@]}"; do
  IFS='|' read -r label url filename expected_size <<< "$spec"
  slug=$(printf '%s' "$label" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-')
  slug=${slug%-}
  result_path="$OUTPUT_ROOT/v3-medium-large-${slug}-${RUN_TAG}/benchmark_v3_results.json"
  model_path="$MODEL_DIR/$filename"

  if result_complete "$result_path"; then
    printf '%s\t%s\tquant_sweep_complete\talready benchmarked\n' \
      "$(date -Is)" "$label" >> "$STATUS_FILE"
    continue
  fi

  current_size=0
  [[ -f "$model_path" ]] && current_size=$(stat -c %s "$model_path")
  remaining=$((expected_size - current_size))
  free_bytes=$(df --output=avail -B1 "$MODEL_DIR" | tail -n 1 | tr -d ' ')
  if (( remaining > 0 && free_bytes < remaining + MIN_FREE_BYTES )); then
    printf '%s\t%s\tinsufficient_space\tneed=%s free=%s reserve=%s\n' \
      "$(date -Is)" "$label" "$remaining" "$free_bytes" "$MIN_FREE_BYTES" >> "$STATUS_FILE"
    exit 1
  fi

  if [[ ! -f "$model_path" ]] || [[ $(stat -c %s "$model_path") -ne $expected_size ]]; then
    printf '%s\t%s\tdownload_start\texpected=%s\n' \
      "$(date -Is)" "$label" "$expected_size" >> "$STATUS_FILE"
    nice -n 19 ionice -c 3 aria2c \
      --dir="$MODEL_DIR" \
      --out="$filename" \
      --continue=true \
      --max-connection-per-server=4 \
      --split=4 \
      --min-split-size=16M \
      --file-allocation=none \
      --auto-file-renaming=false \
      --allow-overwrite=false \
      --all-proxy="$PROXY" \
      --summary-interval=30 \
      "$url"
  fi

  actual_size=$(stat -c %s "$model_path")
  if [[ "$actual_size" -ne "$expected_size" ]]; then
    printf '%s\t%s\tsize_mismatch\texpected=%s actual=%s\n' \
      "$(date -Is)" "$label" "$expected_size" "$actual_size" >> "$STATUS_FILE"
    exit 1
  fi

  escaped_model=$(python3 - "$label" <<'PY'
import re
import sys
print(re.escape(sys.argv[1]))
PY
  )
  OUTPUT_ROOT="$OUTPUT_ROOT" \
  RUN_TAG="$RUN_TAG" \
  RUNS=1 \
  MODEL_FILTER="^${escaped_model}$" \
  PORT="$PORT" \
  bash "$RUNNER"

  if ! result_complete "$result_path"; then
    printf '%s\t%s\tbenchmark_incomplete\t%s\n' \
      "$(date -Is)" "$label" "$result_path" >> "$STATUS_FILE"
    exit 1
  fi

  if [[ "$KEEP_ARTIFACTS" == 1 ]]; then
    printf '%s\t%s\tquant_sweep_complete\tartifact retained\n' \
      "$(date -Is)" "$label" >> "$STATUS_FILE"
  else
    rm -f -- "$model_path" "$model_path.aria2"
    printf '%s\t%s\tquant_sweep_complete\tartifact removed after verified result\n' \
      "$(date -Is)" "$label" >> "$STATUS_FILE"
  fi
done
