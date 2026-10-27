#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}
BUNKER_DATA_ROOT=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
BUNKER_RELEASE_MEDIA_ROOT=${BUNKER_RELEASE_MEDIA_ROOT:-"$HOME/releases/media"}

SERVER_DEFAULT=${SERVER_DEFAULT:-"$HOME/llama.cpp-upstream-20261015/build-vulkan/bin/llama-server"}
SERVER_GLM53=${SERVER_GLM53:-"$HOME/llama.cpp-glm53-reap50/build-vulkan/bin/llama-server"}
SERVER_FLINT=${SERVER_FLINT:-"$HOME/llama.cpp-flint-20261026/build-vulkan/bin/llama-server"}
RUNNER="$BENCH_ROOT/scripts/benchmarking/bunker_benchmark_v3.py"
SUITE="$BENCH_ROOT/scripts/benchmarking/corpora/bunker_benchmark_v3.json"
OUTPUT_ROOT=${OUTPUT_ROOT:-${BUNKER_DATA_ROOT}/benchmarks/bunker-v3-medium-large-20261019}
RUN_TAG=${RUN_TAG:-20261019}
RUNS=${RUNS:-1}
MIMO_MOE_CACHE_MIB=${MIMO_MOE_CACHE_MIB:-8192}
MIMO_GPU_LAYERS=${MIMO_GPU_LAYERS:-all}
CASE_TIMEOUT=${CASE_TIMEOUT:-600}
MODEL_FILTER=${MODEL_FILTER:-}
MODEL_SPECS_FILE=${MODEL_SPECS_FILE:-}
QUEUE_WAIT=${QUEUE_WAIT:-0}
CASE_ID=${CASE_ID:-}
TRACK=${TRACK:-}
PORT=${PORT:-18081}

mkdir -p "$OUTPUT_ROOT/logs"
touch "$OUTPUT_ROOT/wave_status.tsv"

exec 9>"$OUTPUT_ROOT/queue.lock"
if ! flock -w "$QUEUE_WAIT" 9; then
  printf '%s\tqueue\talready_running\n' "$(date -Is)" >> "$OUTPUT_ROOT/wave_status.tsv"
  exit 0
fi

# label|model|profile|server|draft-model
# Representative models run first. Additional quantizations follow after the
# architecture-level results so an interrupted wave still produces useful data.
MODELS=(
  "Spark-X2.6-4B-Q5_K_M|${BUNKER_DATA_ROOT}/models/spark-x2.6-4b/Spark-X2.6-4B-Q5_K_M.gguf|plain|flint|"
  "Flint-Q4_K_M|${BUNKER_DATA_ROOT}/models/flint/Flint-Q4_K_M.gguf|plain|flint|"
  "Nanbeige4.3-33B-Q4_K_M|${BUNKER_DATA_ROOT}/models/nanbeige4.3-33b/Nanbeige_Nanbeige4.3-33B-Q4_K_M.gguf|plain|flint|"
  "LFM2.5-24B-A2B-Q4_K_M|${BUNKER_DATA_ROOT}/models/lfm2.5-24b-a2b-ggml-org/LFM2.5-24B-A2B-Q4_K_M.gguf|plain|default|"
  "gemma-4-26B-A4B-it-UD-Q4_K_M|${BUNKER_DATA_ROOT}/models/gemma-4-26b-a4b/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf|plain|flint|"
  "Qwen3.6-27B-Q4_K_M-MTP|${BUNKER_DATA_ROOT}/models/qwen3.6-27b-mtp-q4-k-m/Qwen3.6-27B-Q4_K_M.gguf|mtp-internal|flint|"
  "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0-MTP|${BUNKER_DATA_ROOT}/models/nemotron-3.5-lightning-ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/nemotron-3.5-lightning-ggml-org/mtp-NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf"
  "Qwen3.6-35B-A3B-UD-Q4_K_M|${BUNKER_DATA_ROOT}/models/qwen3.6-35b-a3b/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf|plain|flint|"
  "gemma-4-31B-it-Q4_K_M|${BUNKER_DATA_ROOT}/models/gemma-4-31b/gemma-4-31B-it-Q4_K_M.gguf|plain|flint|"
  "gemma-4-31B-it-Q5_K_M|${BUNKER_DATA_ROOT}/models/gemma-4-31b/gemma-4-31B-it-Q5_K_M.gguf|plain|flint|"
  "gemma-4-31B-it-Q6_K|${BUNKER_DATA_ROOT}/models/gemma-4-31b/gemma-4-31B-it-Q6_K.gguf|plain|flint|"
  "Qwen3.8-27B-UD-Q6_K_M-MTP|${BUNKER_DATA_ROOT}/models/qwen3.8-27b-unsloth/Qwen3.8-27B-UD-Q6_K_M.gguf|mtp-external|flint|${BUNKER_DATA_ROOT}/models/qwen3.8-27b-unsloth/mtp-Qwen3.8-27B-Q4_0.gguf"
  "Qwen3.8-27B-Q4_K_M|${BUNKER_DATA_ROOT}/models/qwen3.8-27b-ggml-org/Qwen3.8-27B-Q4_K_M.gguf|plain|flint|"
  "gemma-4-E4B-it-Q4_K_M|${BUNKER_DATA_ROOT}/models/local-imports/gemma-4-E4B-it-Q4_K_M.gguf|plain|flint|"
  "Qwen3-14B-Q4_K_M|${BUNKER_DATA_ROOT}/models/qwen3-14b/Qwen3-14B-Q4_K_M.gguf|plain|flint|"
  "Qwen3.5-9B-Q5_K_M|${BUNKER_DATA_ROOT}/models/local-imports/Qwen3.5-9B-Q5_K_M.gguf|plain|flint|"
  "Qwen3.8-27B-Uncensored-Q6_K-MTP|${BUNKER_DATA_ROOT}/models/qwen3.8-27b-uncensored/Qwen3.8-27B-Uncensored-Q6_K.gguf|mtp-internal|flint|"
  "Qwen3.6-27B-Abliterated-Q4_K_M-MTP|${BUNKER_DATA_ROOT}/models/qwen3.6-27b-abliterated-mtp/Qwen3.6-27B-abliterated-Gaston-MTP-Q4_K_M.gguf|mtp-internal|flint|"
  "Qwen3-Coder-Next-Q4_K_M|${BUNKER_DATA_ROOT}/models/qwen3-coder-next-q4-k-m/Qwen3-Coder-Next-Q4_K_M.gguf|plain|default|"
  "Llama-3.3-70B-Instruct-Q4_K_M|${BUNKER_DATA_ROOT}/models/llama-3.3-70b-instruct-q4-k-m/Llama-3.3-70B-Instruct-Q4_K_M.gguf|plain|default|"
  "Sakura-MiMo-V2.6-Flash-MOPD-P160-IQ2_XS|${BUNKER_DATA_ROOT}/models/sakura-mimo-v2.6-flash-mopd-p160/MiMo-V2.6-Flash-MOPD-P160-OnPolicy-v3la-IQ2_XS.gguf|plain|default|"
  "MiMo-V2.6-Flash-MOPD-full-Q3_K|${BUNKER_DATA_ROOT}/models/mimo-v2.6-flash-mopd-q3/MiMo-V2.6-Flash-MOPD-3.61bpw-Q3_K.gguf|plain|mimo-stream|"
  "Mistral-Medium-3.5-128B-Q3_K_M|${BUNKER_DATA_ROOT}/models/mistral-medium-3.5-128b-q3-k-m/Mistral-Medium-3.5-128B-Q3_K_M-00001-of-00003.gguf|plain|default|"
  "Qwen3.5-122B-A10B-Q3_K_M|${BUNKER_DATA_ROOT}/models/qwen3.5-122b-a10b-q3-k-m/Qwen3.5-122B-A10B-Q3_K_M-00001-of-00003.gguf|plain|default|"
  "Qwen3.5-122B-A10B-UD-IQ4_NL-MTP|${BUNKER_DATA_ROOT}/models/qwen3.5-122b-a10b-mtp-ud-iq4-nl/Qwen3.5-122B-A10B-UD-IQ4_NL-00001-of-00003.gguf|mtp-internal|default|"
  "NVIDIA-Nemotron-3-Super-120B-A12B-UD-Q3_K_M|${BUNKER_DATA_ROOT}/models/nvidia-nemotron-3-super-120b-a12b-ud-q3-k-m/NVIDIA-Nemotron-3-Super-120B-A12B-UD-Q3_K_M-00001-of-00003.gguf|plain|default|"
  "NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-Q4_0-MTP|${BUNKER_DATA_ROOT}/models/nemotron-3.5-super-vl-ggml-org-q4/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-Q4_0.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/nemotron-3.5-super-vl-ggml-org-q4/mtp-NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-Q4_0.gguf"
  "GLM-5.3-Flash-REAP50-Q3_K_M|${BUNKER_DATA_ROOT}/models/glm-5.3-flash-reap50-q3-k-m/GLM-5.3-Flash-REAP50-Q3_K_M.gguf|plain|glm53|"
  "MiniMax-M2.7-Q2_K|${BUNKER_DATA_ROOT}/models/minimax-m2.7-q2-k/MiniMax-M2.7-Q2_K-00001-of-00002.gguf|plain|default|"
  "Qwen3.8-Flash-Next-Q2_K-MTP|${BUNKER_DATA_ROOT}/models/qwen3.8-flash-next-ggml-org-q2/Qwen3.8-Flash-Next-Q2_K-00001-of-00002.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/qwen3.8-flash-next-ggml-org-q2/mtp-Qwen3.8-Flash-Next-Q4_0.gguf"
  "Qwen3.8-Flash-Next-UD-IQ3_XXS-MTP|${BUNKER_DATA_ROOT}/models/qwen3.8-flash-next-unsloth-iq3/Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00003.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/qwen3.8-flash-next-unsloth-iq3/mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf"
  "NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-UD-Q4_K_XL-MTP|${BUNKER_DATA_ROOT}/models/nemotron-3.5-super-vl-unsloth-q4/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-UD-Q4_K_XL-00001-of-00003.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/nemotron-3.5-super-vl-ggml-org-q4/mtp-NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-Q4_0.gguf"
  "LFM2.5-24B-A2B-UD-Q6_K_XL|${BUNKER_DATA_ROOT}/models/lfm2.5-24b-a2b-unsloth/LFM2.5-24B-A2B-UD-Q6_K_XL.gguf|plain|default|"
  "gemma-4-26B-A4B-it-UD-Q5_K_M|${BUNKER_RELEASE_MEDIA_ROOT}/amd395-full-rc1/models/gemma-4-26B-A4B-it-UD-Q5_K_M.gguf|plain|flint|"
  "Qwen3.6-35B-A3B-UD-Q5_K_M-MTP|${BUNKER_RELEASE_MEDIA_ROOT}/amd395-full-rc1/models/Qwen3.6-35B-A3B-UD-Q5_K_M.gguf|mtp-internal|flint|"
  "Qwen3.6-35B-A3B-UD-Q6_K-MTP|${BUNKER_DATA_ROOT}/models/qwen3.6-35b-a3b-mtp/Qwen3.6-35B-A3B-UD-Q6_K.gguf|mtp-internal|flint|"
  "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q6_K_XL-MTP|${BUNKER_DATA_ROOT}/models/nemotron-3.5-lightning-unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q6_K_XL.gguf|mtp-external|default|${BUNKER_DATA_ROOT}/models/nemotron-3.5-lightning-ggml-org/mtp-NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf"
  "Huihui-Qwen3.6-35B-A3B-abliterated-Q4_K-MTP|${BUNKER_DATA_ROOT}/models/huihui-qwen3.6-35b-a3b-abliterated-mtp-q4-k/Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q4_K.gguf|mtp-internal|flint|"
  "Huihui-Qwen3.6-35B-A3B-abliterated-Q6_K-MTP|${BUNKER_DATA_ROOT}/models/quant-sweep-temp/Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q6_K.gguf|mtp-internal|flint|"
  "Huihui-Qwen3.6-35B-A3B-abliterated-Q8_0-MTP|${BUNKER_DATA_ROOT}/models/quant-sweep-temp/Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q8_0.gguf|mtp-internal|flint|"
  "gemma-4-26B-A4B-it-UD-Q3_K_M|${BUNKER_DATA_ROOT}/models/local-imports/gemma-4-26B-A4B-it-UD-Q3_K_M.gguf|plain|flint|"
  "gemma-4-31B-it-uncensored-heretic-Q4_K_M|${BUNKER_DATA_ROOT}/models/local-imports/gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf|plain|flint|"
  "Qwen3.6-27B-Q4_K_M|${BUNKER_DATA_ROOT}/models/qwen3.6-27b/Qwen3.6-27B-Q4_K_M.gguf|plain|flint|"
  "Qwen3.6-27B-UD-IQ3_XXS-MTP|${BUNKER_DATA_ROOT}/models/qwen3.6-27b-mtp/Qwen3.6-27B-UD-IQ3_XXS.gguf|mtp-internal|flint|"
  "Qwen3.6-27B-UD-IQ2_M|${BUNKER_DATA_ROOT}/models/local-imports/Qwen3.6-27B-UD-IQ2_M.gguf|plain|flint|"
  "Qwen3.6-35B-A3B-Uncensored-Q3_K_P|${BUNKER_DATA_ROOT}/models/local-imports/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q3_K_P.gguf|plain|flint|"
  "Qwen3.6-35B-A3B-Uncensored-Q6_K_P|${BUNKER_DATA_ROOT}/models/quant-sweep-temp/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf|plain|flint|"
  "Qwen3.6-35B-A3B-Uncensored-Q8_K_P|${BUNKER_DATA_ROOT}/models/quant-sweep-temp/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf|plain|flint|"
)

if [[ -n "$MODEL_SPECS_FILE" ]]; then
  if [[ ! -f "$MODEL_SPECS_FILE" ]]; then
    printf '%s\tqueue\tmissing_model_specs\t%s\n' \
      "$(date -Is)" "$MODEL_SPECS_FILE" >> "$OUTPUT_ROOT/wave_status.tsv"
    exit 1
  fi
  mapfile -t MODELS < <(awk 'NF && $1 !~ /^#/' "$MODEL_SPECS_FILE")
fi

server_pid=''
cleanup_server() {
  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  server_pid=''
}
trap cleanup_server EXIT
trap 'cleanup_server; exit 130' INT
trap 'cleanup_server; exit 143' TERM

for spec in "${MODELS[@]}"; do
  IFS='|' read -r label model_path profile server_kind draft_path <<< "$spec"
  model_path=${model_path//__BUNKER_DATA_ROOT__/$BUNKER_DATA_ROOT}
  model_path=${model_path//__BUNKER_RELEASE_MEDIA_ROOT__/$BUNKER_RELEASE_MEDIA_ROOT}
  draft_path=${draft_path//__BUNKER_DATA_ROOT__/$BUNKER_DATA_ROOT}
  draft_path=${draft_path//__BUNKER_RELEASE_MEDIA_ROOT__/$BUNKER_RELEASE_MEDIA_ROOT}
  if [[ -n "$MODEL_FILTER" ]] && [[ ! "$label" =~ $MODEL_FILTER ]]; then
    continue
  fi
  slug=$(printf '%s' "$label" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-')
  slug=${slug%-}
  run_id="v3-medium-large-${slug}-${RUN_TAG}"
  log_path="$OUTPUT_ROOT/logs/${slug}.server.log"
  result_path="$OUTPUT_ROOT/$run_id/benchmark_v3_results.json"

  if [[ -f "$result_path" ]] && python3 - "$result_path" "$RUNS" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
wanted = int(sys.argv[2])
complete = sum(1 for run in d.get("runs", []) if len(run.get("cases", [])) == 20)
raise SystemExit(0 if complete >= wanted else 1)
PY
  then
    printf '%s\t%s\tcomplete\talready has %s full runs\n' "$(date -Is)" "$label" "$RUNS" >> "$OUTPUT_ROOT/wave_status.tsv"
    continue
  fi

  if [[ ! -s "$model_path" ]]; then
    printf '%s\t%s\tmissing\t%s\n' "$(date -Is)" "$label" "$model_path" >> "$OUTPUT_ROOT/wave_status.tsv"
    continue
  fi
  if [[ "$profile" == mtp-external && ! -s "$draft_path" ]]; then
    printf '%s\t%s\tmissing_draft\t%s\n' "$(date -Is)" "$label" "$draft_path" >> "$OUTPUT_ROOT/wave_status.tsv"
    continue
  fi

  server_bin=$SERVER_DEFAULT
  if [[ "$server_kind" == glm53 ]]; then
    server_bin=$SERVER_GLM53
  elif [[ "$server_kind" == flint || "$server_kind" == mimo-stream ]]; then
    server_bin=$SERVER_FLINT
  fi
  if [[ ! -x "$server_bin" ]]; then
    printf '%s\t%s\tmissing_runtime\t%s\n' "$(date -Is)" "$label" "$server_bin" >> "$OUTPUT_ROOT/wave_status.tsv"
    continue
  fi

  cleanup_server
  server_extra=()
  if [[ "$profile" == mtp-internal || "$profile" == mtp-external ]]; then
    server_extra+=(
      --spec-type draft-mtp
      --spec-draft-n-max 4
      --spec-draft-n-min 1
      --spec-draft-p-min 0.75
    )
  fi
  if [[ "$profile" == mtp-external ]]; then
    server_extra+=(--spec-draft-model "$draft_path" --spec-draft-ngl all)
  fi
  if [[ "$server_kind" == mimo-stream ]]; then
    server_extra+=(
      --load-mode mmap
      --lazy-mode on
      --cpu-moe
      --moe-cache-mib "$MIMO_MOE_CACHE_MIB"
      --fit off
    )
  elif [[ "$server_kind" != glm53 ]]; then
    server_extra+=(--load-mode none)
  fi

  printf '%s\t%s\tstarting\t%s\n' "$(date -Is)" "$label" "$profile" >> "$OUTPUT_ROOT/wave_status.tsv"
  server_gpu_layers=all
  if [[ "$server_kind" == mimo-stream ]]; then
    server_gpu_layers=$MIMO_GPU_LAYERS
  fi
  "$server_bin" \
    --model "$model_path" \
    --alias "$label" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --ctx-size 32768 \
    --parallel 1 \
    --device Vulkan0 \
    --gpu-layers "$server_gpu_layers" \
    --flash-attn on \
    --batch-size 1024 \
    --ubatch-size 512 \
    --cont-batching \
    --jinja \
    --chat-template-kwargs '{"enable_thinking":false}' \
    --reasoning off \
    --reasoning-budget 0 \
    "${server_extra[@]}" \
    > "$log_path" 2>&1 &
  server_pid=$!

  ready=0
  for _ in $(seq 1 1200); do
    if ! kill -0 "$server_pid" 2>/dev/null; then
      break
    fi
    if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 1
  done

  if [[ "$ready" -ne 1 ]]; then
    detail=$(tail -n 5 "$log_path" | tr '\n' ' ' | cut -c1-600)
    printf '%s\t%s\tload_failed\t%s\n' "$(date -Is)" "$label" "$detail" >> "$OUTPUT_ROOT/wave_status.tsv"
    cleanup_server
    continue
  fi

  runner_extra=()
  if [[ -n "$CASE_ID" ]]; then
    runner_extra+=(--case-id "$CASE_ID")
  fi
  if [[ -n "$TRACK" ]]; then
    runner_extra+=(--track "$TRACK")
  fi

  if python3 "$RUNNER" \
    --suite "$SUITE" \
    --api-url "http://127.0.0.1:${PORT}/v1/chat/completions" \
    --model "$label" \
    --runs "$RUNS" \
    --temperature 0.05 \
    --max-tokens 8192 \
    --case-timeout "$CASE_TIMEOUT" \
    --output-dir "$OUTPUT_ROOT" \
    --run-id "$run_id" \
    --resume \
    "${runner_extra[@]}" \
    > "$OUTPUT_ROOT/logs/${slug}.benchmark.log" 2>&1; then
    printf '%s\t%s\tcomplete\t%s\n' "$(date -Is)" "$label" "$run_id" >> "$OUTPUT_ROOT/wave_status.tsv"
  else
    status=$?
    printf '%s\t%s\tbenchmark_failed\texit=%s\n' "$(date -Is)" "$label" "$status" >> "$OUTPUT_ROOT/wave_status.tsv"
  fi
  cleanup_server
done

printf '%s\twave\tfinished\tfilter=%s\n' "$(date -Is)" "${MODEL_FILTER:-all}" >> "$OUTPUT_ROOT/wave_status.tsv"
trap - EXIT INT TERM
cleanup_server
