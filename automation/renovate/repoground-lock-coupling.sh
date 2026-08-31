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
changed_paths="$(git diff --name-only --diff-filter=ACMRTUXB HEAD --)"

# Renovate can revisit an existing update branch whose dependency change is
# already committed in HEAD. Compare the whole branch delta against main as
# well as the current worktree so the hook remains self-healing across runs.
if git show-ref --verify --quiet refs/remotes/origin/main; then
  merge_base="$(git merge-base HEAD refs/remotes/origin/main)"
  branch_paths="$(git diff --name-only --diff-filter=ACMRTUXB "$merge_base" HEAD --)"
  if [[ -n "$branch_paths" ]]; then
    changed_paths+=$'\n'"$branch_paths"
  fi
else
  echo "RepoGround lock coupling: origin/main unavailable; regenerating fail-safe" >&2
  needs_lock_refresh=true
fi

if [[ "$needs_lock_refresh" != true ]]; then
  while IFS= read -r path; do
    case "$path" in
      requirements*.txt | requirements/*)
        needs_lock_refresh=true
        break
        ;;
    esac
  done <<< "$changed_paths"
fi

if [[ "$needs_lock_refresh" != true ]]; then
  echo "RepoGround lock coupling: no Python requirement change on branch; nothing to regenerate"
  exit 0
fi

generator="scripts/release/compile_dependency_locks.sh"
if [[ ! -f "$generator" ]]; then
  echo "RepoGround lock coupling refused: canonical generator is missing" >&2
  exit 2
fi

bash "$generator"
bash "$generator" --check
