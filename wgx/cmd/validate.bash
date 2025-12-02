#!/usr/bin/env bash
set -euo pipefail

cmd_validate() {
  echo "Check: repos.yml parse"
  python3 "$REPO_CONFIG" --file "$REPOS_YML" validate > /dev/null
  echo "OK."
}
