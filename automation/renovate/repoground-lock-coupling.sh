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

# Renovate invokes this wrapper through RepoGround's postUpgradeTasks contract.
# That invocation is the authoritative trigger. Do not add a second git-diff gate:
# Renovate may already have staged or otherwise normalized its dependency update,
# while the canonical lock generator still needs to refresh derived lock artifacts.
generator="scripts/release/compile_dependency_locks.sh"
if [[ ! -f "$generator" ]]; then
  echo "RepoGround lock coupling refused: canonical generator is missing" >&2
  exit 2
fi

bash "$generator"
bash "$generator" --check
