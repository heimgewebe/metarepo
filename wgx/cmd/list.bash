#!/usr/bin/env bash
set -euo pipefail

cmd_list() {
  echo "▶ Fleet-Repos:"
  python3 "$REPO_CONFIG" --file "$REPOS_YML" repo-rows |
    while IFS=$'\t' read -r name branch url deps; do
      [[ -z "$name" ]] && continue
      local line=" - ${name}"
      [[ -n "$branch" ]] && line+=" [branch: ${branch}]"
      [[ -n "$url" ]] && line+=" → ${url}"
      if [[ -n "$deps" ]]; then
        local d="${deps//,/ , }"
        d="${d// , /, }"
        line+=" (depends_on: ${d})"
      fi
      echo "$line"
    done
}
