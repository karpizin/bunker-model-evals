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
STATUS_FILE="$OUTPUT_ROOT/october_wave_status.tsv"

printf '%s\tgemma-retest\tbenchmark_start\t26b-q3-q4-q5+31b-q4-q5-q6\n' "$(date -Is)" >> "$STATUS_FILE"

OUTPUT_ROOT="$OUTPUT_ROOT" \
RUN_TAG="$RUN_TAG" \
RUNS=1 \
MODEL_FILTER='^(gemma-4-26B-A4B-it-UD-Q3_K_M|gemma-4-26B-A4B-it-UD-Q4_K_M|gemma-4-26B-A4B-it-UD-Q5_K_M|gemma-4-31B-it-Q4_K_M|gemma-4-31B-it-Q5_K_M|gemma-4-31B-it-Q6_K)$' \
PORT="$PORT" \
bash "$RUNNER"

printf '%s\tgemma-retest\tbenchmark_finished\t26b-q3-q4-q5+31b-q4-q5-q6\n' "$(date -Is)" >> "$STATUS_FILE"
