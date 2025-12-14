#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TEMPLATE=".devcontainer/_setup-wgx-bridge.template.sh"
PATCHER=".devcontainer/_wgx-bridge-patch-devcontainer-json.py"

usage() {
  cat <<'USAGE'
Usage:
  .devcontainer/sync-wgx-bridge-to-fleet.sh <repo-dir> [<repo-dir>...]

Examples:
  .devcontainer/sync-wgx-bridge-to-fleet.sh ../hausKI ../chronik ../semantAH
  .devcontainer/sync-wgx-bridge-to-fleet.sh /workspaces/hausKI /workspaces/chronik

What it does:
  - writes .devcontainer/setup-wgx-bridge.sh from the metarepo template
  - patches .devcontainer/devcontainer.json postCreateCommand to call it (conservatively)
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -lt 1 ]]; then
  usage
  exit 0
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "::error::Missing template: $TEMPLATE" >&2
  exit 1
fi
if [[ ! -f "$PATCHER" ]]; then
  echo "::error::Missing patcher: $PATCHER" >&2
  exit 1
fi

sync_one() {
  local repo="$1"
  local dc_dir="$repo/.devcontainer"
  local dc_json="$dc_dir/devcontainer.json"
  local out="$dc_dir/setup-wgx-bridge.sh"

  if [[ ! -d "$dc_dir" ]]; then
    echo "skip: $repo (no .devcontainer/)"
    return 0
  fi

  mkdir -p "$dc_dir"
  install -m 0755 "$TEMPLATE" "$out"
  echo "write: $out"

  if [[ -f "$dc_json" ]]; then
    python3 "$PATCHER" "$dc_json" || true
    echo "patch: $dc_json (postCreateCommand)"
  else
    echo "note: $repo has no .devcontainer/devcontainer.json (script copied anyway)"
  fi
}

for repo in "$@"; do
  sync_one "$repo"
done

echo "Done."
