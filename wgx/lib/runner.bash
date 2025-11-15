#!/usr/bin/env bash

wgx_run_task() {
  local task_name="$1"
  local profile_file="./.wgx/profile.yml"
  local yq_bin="./tools/bin/yq"

  if [[ ! -x "$yq_bin" ]]; then
      die "yq binary not found at $yq_bin. Please run scripts/tools/yq-pin.sh"
  fi

  if [[ ! -f "$profile_file" ]]; then
    die "Profile file not found: $profile_file"
  fi

  local task_script
  task_script=$("$yq_bin" eval ".tasks.$task_name" "$profile_file")

  if [[ -z "$task_script" || "$task_script" == "null" ]]; then
    log "Task '$task_name' not found or is empty in profile."
    return 0
  fi

  bash -c "$task_script"
}
