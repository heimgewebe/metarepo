#!/usr/bin/env bash
set -euo pipefail

cmd_run(){
  local target="${1:-ci}"
  need gh
  local repos_to_run; mapfile -t repos_to_run < <(ordered_repos)
  local total=${#repos_to_run[@]} i=0
  for r in "${repos_to_run[@]}"; do
    (( i++ ))
    echo "▸ [$i/$total] $r → $target"
    if gh workflow list --repo "$(owner)/$r" --limit 200 | awk '{print $1}' | grep -qx "$target"; then
      if ! gh workflow run "$target" --repo "$(owner)/$r"; then
        echo "Workflow-Start in $r übersprungen oder fehlgeschlagen."
      fi
    else
      echo "⚠︎ Workflow '$target' existiert nicht in $r – übersprungen."
    fi
  done
}
