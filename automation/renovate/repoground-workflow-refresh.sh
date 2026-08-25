#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

origin="$(git config --get remote.origin.url || true)"
if [[ ! "$origin" =~ ^https://([^/@]+@)?github\.com/heimgewebe/repoground(\.git)?$ ]] &&
  [[ ! "$origin" =~ ^git@github\.com:heimgewebe/repoground(\.git)?$ ]] &&
  [[ ! "$origin" =~ ^ssh://git@github\.com/heimgewebe/repoground(\.git)?$ ]]; then
  echo "RepoGround workflow refresh refused: current repository is not heimgewebe/repoground" >&2
  exit 2
fi

refresh="scripts/ci/refresh_workflow_control_plane.py"
if [[ ! -f "$refresh" ]]; then
  echo "RepoGround workflow refresh refused: canonical refresh script is missing" >&2
  exit 2
fi

python3 "$refresh"
