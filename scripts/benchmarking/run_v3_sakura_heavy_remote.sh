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

LABEL='MiMo-V2.6-Flash-MOPD-full-Q3_K'
MODEL_PATH="${BUNKER_DATA_ROOT}/models/mimo-v2.6-flash-mopd-q3/MiMo-V2.6-Flash-MOPD-3.61bpw-Q3_K.gguf"
EXPECTED_SIZE=139630709088

if [[ ! -f "$MODEL_PATH" ]]; then
  printf '%s\t%s\tmissing\t%s\n' \
    "$(date -Is)" "$LABEL" "$MODEL_PATH" >> "$OUTPUT_ROOT/october_wave_status.tsv"
  exit 1
fi

actual_size=$(stat -c %s "$MODEL_PATH")
if [[ "$actual_size" -ne "$EXPECTED_SIZE" ]]; then
  printf '%s\t%s\tsize_mismatch\texpected=%s actual=%s\n' \
    "$(date -Is)" "$LABEL" "$EXPECTED_SIZE" "$actual_size" >> "$OUTPUT_ROOT/october_wave_status.tsv"
  exit 1
fi

escaped_model=$(python3 - "$LABEL" <<'PY'
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

slug=$(printf '%s' "$LABEL" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-')
slug=${slug%-}
result_path="$OUTPUT_ROOT/v3-medium-large-${slug}-${RUN_TAG}/benchmark_v3_results.json"
python3 - "$result_path" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)
complete = sum(1 for run in payload.get("runs", []) if len(run.get("cases", [])) == 20)
raise SystemExit(0 if complete >= 1 else 1)
PY
