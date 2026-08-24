#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

origin="$(git config --get remote.origin.url || true)"
if [[ ! "$origin" =~ ^https://([^/@]+@)?github\.com/heimgewebe/repoground(\.git)?$ ]] &&
  [[ ! "$origin" =~ ^git@github\.com:heimgewebe/repoground(\.git)?$ ]] &&
  [[ ! "$origin" =~ ^ssh://git@github\.com/heimgewebe/repoground(\.git)?$ ]]; then
  echo "RepoGround lock coupling refused: current repository is not heimgewebe/repoground" >&2
  exit 2
fi

needs_lock_refresh=false
while IFS= read -r path; do
  case "$path" in
    requirements*.txt | requirements/*)
      needs_lock_refresh=true
      break
      ;;
  esac
done < <(git diff --name-only --diff-filter=ACMRTUXB HEAD --)

if [[ "$needs_lock_refresh" != true ]]; then
  echo "RepoGround lock coupling: no Python requirement change; nothing to regenerate"
  exit 0
fi

generator="scripts/release/compile_dependency_locks.sh"
if [[ ! -f "$generator" ]]; then
  echo "RepoGround lock coupling refused: canonical generator is missing" >&2
  exit 2
fi

bash "$generator"
bash "$generator" --check
