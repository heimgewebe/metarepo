#!/usr/bin/env bash
set -euo pipefail

wgx_run_task() {
  local task_name="$1"
  local profile_file="./.wgx/profile.yml"
  local yq_bin="./tools/bin/yq"

  if [[ ! -x "$yq_bin" ]]; then
    # Fallback to system yq if the pinned one isn't there
    if command -v yq > /dev/null 2>&1; then
      yq_bin=$(command -v yq)
    else
      die "yq binary not found. Please run scripts/tools/yq-pin.sh or install yq."
    fi
  fi

  if [[ ! -f "$profile_file" ]]; then
    die "Profile file not found: $profile_file"
  fi

  local task_script
  # Use eval to handle multi-line scripts correctly from yq output
  task_script=$("$yq_bin" -r ".tasks.$task_name" "$profile_file")

  if [[ -z "$task_script" || "$task_script" == "null" ]]; then
    log "Task '$task_name' not found or is empty in profile."
    return 0
  fi

  bash -c "$task_script"
}
