#!/usr/bin/env bash
set -euo pipefail

data_root=${BUNKER_DATA_ROOT:-"$HOME/bunker-data"}
queue_root=${QUEUE_ROOT:-"$data_root/benchmarks/bunker-v3-nemotron-bolt-q4-download"}
model_dir="$data_root/models/nvidia-nemotron-3.5-bolt-74b-q4"
target_file="$model_dir/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-AD-IQ4_XS.gguf"
expected_size=46568598432
expected_sha256=a74d21cd56ef59d00b2b58fb6afa1b721692e034a487d0212a63c1ed1d7e2634
reserve_bytes=${RESERVE_BYTES:-6442450944}
source_url='https://huggingface.co/AtomicChat/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF/resolve/dc8110a7e7fd4c1f35191a7e8842a94518c4a6d1/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-AD-IQ4_XS.gguf?download=true'

mkdir -p "$queue_root" "$model_dir"
exec >>"$queue_root/download.log" 2>&1

printf '%s queued target=%s expected_bytes=%s\n' \
  "$(date -Is)" "$target_file" "$expected_size"

while pgrep -f 'bunker_benchmark_v3.py' >/dev/null 2>&1 || \
      pgrep -f 'run_v3_medium_large_remote.sh' >/dev/null 2>&1; do
  printf '%s waiting_for_benchmarks\n' "$(date -Is)"
  sleep 30
done

required_bytes=$((expected_size + reserve_bytes))
while :; do
  available_bytes=$(df --output=avail -B1 "$data_root" | tail -1 | tr -d ' ')
  if [[ "$available_bytes" -ge "$required_bytes" ]]; then
    break
  fi
  printf '%s waiting_for_space available=%s required_with_reserve=%s\n' \
    "$(date -Is)" "$available_bytes" "$required_bytes"
  sleep 60
done

if [[ -f "$target_file" ]] && \
   [[ $(stat -c %s "$target_file") -eq "$expected_size" ]] && \
   printf '%s  %s\n' "$expected_sha256" "$target_file" | sha256sum --check --status; then
  printf '%s already_complete bytes=%s sha256=%s\n' \
    "$(date -Is)" "$expected_size" "$expected_sha256"
  exit 0
fi

aria2_args=(
  --continue=true
  --max-connection-per-server=4
  --split=4
  --min-split-size=16M
  --file-allocation=none
  --auto-file-renaming=false
  --allow-overwrite=false
  --summary-interval=30
  --dir="$model_dir"
  --out="$(basename "$target_file")"
)
if [[ -n ${ARIA2_PROXY:-} ]]; then
  aria2_args+=(--all-proxy="$ARIA2_PROXY")
fi

printf '%s download_started\n' "$(date -Is)"
aria2c "${aria2_args[@]}" "$source_url"

actual_size=$(stat -c %s "$target_file")
if [[ "$actual_size" -ne "$expected_size" ]]; then
  printf '%s size_mismatch expected=%s actual=%s\n' \
    "$(date -Is)" "$expected_size" "$actual_size"
  exit 21
fi
printf '%s  %s\n' "$expected_sha256" "$target_file" | sha256sum --check --status
printf '%s download_finished bytes=%s sha256=%s\n' \
  "$(date -Is)" "$actual_size" "$expected_sha256"
