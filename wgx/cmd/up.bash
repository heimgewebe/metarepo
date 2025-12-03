#!/usr/bin/env bash
set -euo pipefail

cmd_up() {
  cmd_plan
  if ((DRYRUN == 1)); then
    echo "⚑ Dry-run aktiv – keine Commits oder Pushes."
  else
    read -p "Fortfahren? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Abgebrochen."
      exit 0
    fi
  fi

  local repos_to_sync
  mapfile -t repos_to_sync < <(ordered_repos)
  local total=${#repos_to_sync[@]} i=0 success_count=0 fail_count=0
  for r in "${repos_to_sync[@]}"; do
    ((i++))
    echo "▸ [$i/$total] Sync $r"
    if copy_templates_into_repo "$r"; then
      ((success_count++))
    else
      ((fail_count++))
    fi
  done
  echo "✔︎ Sync abgeschlossen. Erfolg: $success_count, Fehler: $fail_count."
}
