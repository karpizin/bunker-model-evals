#!/usr/bin/env bash
set -uo pipefail

worker=${1:?usage: run_v3_remote_supervisor.sh WORKER}
llama_was_active=0
soak_was_active=0
systemctl is-active --quiet bunker-llama-vulkan.service && llama_was_active=1
systemctl is-active --quiet bunker-acceptance-soak.service && soak_was_active=1

restore_services() {
  if [[ "$llama_was_active" -eq 1 ]]; then
    systemctl start bunker-llama-vulkan.service || true
  fi
  if [[ "$soak_was_active" -eq 1 ]]; then
    systemctl start bunker-acceptance-soak.service || true
  fi
}

trap restore_services EXIT INT TERM
systemctl stop bunker-acceptance-soak.service
systemctl stop bunker-llama-vulkan.service

runuser -u bunkerai -- "$worker"
