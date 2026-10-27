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

# Refresh strong candidates from earlier waves on the current runtime before
# selecting the stability top ten. Models already present in this output root
# are skipped by the shared runner.
MODELS=(
  'Qwen3.8-27B-Q4_K_M'
  'gemma-4-E4B-it-Q4_K_M'
  'Qwen3-14B-Q4_K_M'
  'Qwen3.5-9B-Q5_K_M'
)

for model in "${MODELS[@]}"; do
  escaped_model=$(python3 - "$model" <<'PY'
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
done
