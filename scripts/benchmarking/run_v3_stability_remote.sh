#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}
BUNKER_DATA_ROOT=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
BUNKER_RELEASE_MEDIA_ROOT=${BUNKER_RELEASE_MEDIA_ROOT:-"$HOME/releases/media"}

OUTPUT_ROOT=${OUTPUT_ROOT:-${BUNKER_DATA_ROOT}/benchmarks/bunker-v3-october-wave-20261026}
RUN_TAG=${RUN_TAG:-20261026-fd8f845}
RUNNER=${RUNNER:-$BENCH_ROOT/scripts/benchmarking/run_v3_medium_large_remote.sh}
LEADER_COUNT=${LEADER_COUNT:-10}
TOTAL_RUNS=${TOTAL_RUNS:-5}
PORT=${PORT:-18081}

STATUS_FILE="$OUTPUT_ROOT/october_wave_status.tsv"
SELECTION_FILE="$OUTPUT_ROOT/stability_leaders.tsv"

python3 - "$OUTPUT_ROOT" "$RUN_TAG" "$LEADER_COUNT" > "$SELECTION_FILE" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
run_tag = sys.argv[2]
leader_count = int(sys.argv[3])
excluded_fragments = ("huihui-", "uncensored", "abliterated", "heretic")
best = {}

for path in root.glob(f"*-{run_tag}/benchmark_v3_results.json"):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        continue
    for run in payload.get("runs", []):
        model = str(run.get("model", ""))
        if not model or any(fragment in model.lower() for fragment in excluded_fragments):
            continue
        if len(run.get("cases", [])) != 20:
            continue
        summary = run.get("summary", {})
        score = summary.get("capability_mean_pct")
        critical = summary.get("critical_failures")
        if score is None or critical is None:
            continue
        candidate = (float(score), int(critical), model)
        previous = best.get(model)
        if previous is None or candidate[0] > previous[0] or (
            candidate[0] == previous[0] and candidate[1] < previous[1]
        ):
            best[model] = candidate

leaders = sorted(best.values(), key=lambda item: (-item[0], item[1], item[2]))[:leader_count]
if len(leaders) < leader_count:
    raise SystemExit(f"only {len(leaders)} complete standard candidates; need {leader_count}")
for score, critical, model in leaders:
    print(f"{model}\t{score:.2f}\t{critical}")
PY

printf '%s\tstability\tselected\t%s leaders, %s total runs\n' \
  "$(date -Is)" "$LEADER_COUNT" "$TOTAL_RUNS" >> "$STATUS_FILE"

while IFS=$'\t' read -r model score critical; do
  escaped_model=$(python3 - "$model" <<'PY'
import re
import sys
print(re.escape(sys.argv[1]))
PY
  )
  printf '%s\t%s\tstability_start\tsingle=%s critical=%s target_runs=%s\n' \
    "$(date -Is)" "$model" "$score" "$critical" "$TOTAL_RUNS" >> "$STATUS_FILE"
  OUTPUT_ROOT="$OUTPUT_ROOT" \
  RUN_TAG="$RUN_TAG" \
  RUNS="$TOTAL_RUNS" \
  MODEL_FILTER="^${escaped_model}$" \
  PORT="$PORT" \
  bash "$RUNNER"
  printf '%s\t%s\tstability_complete\ttotal_runs=%s\n' \
    "$(date -Is)" "$model" "$TOTAL_RUNS" >> "$STATUS_FILE"
done < "$SELECTION_FILE"

printf '%s\tstability\tfinished\tleaders=%s runs=%s\n' \
  "$(date -Is)" "$LEADER_COUNT" "$TOTAL_RUNS" >> "$STATUS_FILE"
