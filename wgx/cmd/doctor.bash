#!/usr/bin/env bash
set -euo pipefail

cmd_doctor(){
  for bin in python3 rsync git yq; do command -v "$bin" >/dev/null || echo "WARN: $bin fehlt"; done
  if [[ "$(mode)" == "github" ]]; then
    for bin in jq gh; do command -v "$bin" >/dev/null || echo "WARN: $bin fehlt"; done
  fi
  echo "owner=$(owner)"
  echo "mode=$(mode)"
  echo "PLAN_LIMIT=${PLAN_LIMIT}"
  command -v gh >/dev/null 2>&1 && gh auth status || true
}
