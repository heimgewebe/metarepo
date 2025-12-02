#!/usr/bin/env bash
set -euo pipefail

cmd_plan() {
  echo "▶ Plan (ohne Klonen/Push):"
  if [[ ! -d "$ROOT_DIR/templates" ]]; then
    echo "  (keine templates/ gefunden)"
    return 0
  fi
  local tmp files_count rest
  tmp="$(mktemp)"
  _tmp_dirs+=("$tmp")
  if ! list_template_files > "$tmp"; then
    echo "  (keine Template-Dateien gefunden)"
    return 0
  fi
  files_count="$(wc -l < "$tmp" | tr -d ' ')"
  if ((files_count == 0)); then
    echo "  (keine Template-Dateien gefunden)"
    return 0
  fi

  ordered_repos | while read -r repo; do
    [[ -z "$repo" ]] && continue
    echo " - $repo"
    echo "   files: $files_count"
    if ((PLAN_LIMIT > 0)); then
      head -n "$PLAN_LIMIT" "$tmp" | sed 's/^/     - /'
      rest=$((files_count - PLAN_LIMIT))
      ((rest > 0)) && printf '     … (+%d weitere)\n' "$rest"
    else
      sed 's/^/     - /' "$tmp"
    fi
  done
}
