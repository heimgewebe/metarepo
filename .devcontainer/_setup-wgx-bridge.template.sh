#!/usr/bin/env bash
set -euo pipefail

# WGX bridge (devcontainer/Codespaces):
# - ensures ~/.local/bin is on PATH
# - exposes /workspaces/wgx/wgx as `wgx` via symlink in ~/.local/bin
#
# This is intentionally "soft": if /workspaces/wgx is not present, we warn but do not fail.

ensure_local_bin_on_path() {
  mkdir -p "$HOME/.local/bin"
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
}

bridge_from_workspace() {
  local src="${1:-/workspaces/wgx}/wgx"
  if [[ -x "$src" ]]; then
    ln -sf "$src" "$HOME/.local/bin/wgx"
    echo "WGX bridged: $src -> $HOME/.local/bin/wgx"
    return 0
  fi
  return 1
}

main() {
  ensure_local_bin_on_path

  if command -v wgx > /dev/null 2>&1; then
    echo "WGX already available: $(command -v wgx)"
    exit 0
  fi

  if bridge_from_workspace "/workspaces/wgx"; then
    exit 0
  fi

  echo "WGX not found (expected /workspaces/wgx/wgx)."
  echo "Hint: open a multi-repo workspace that includes the 'wgx' repo."
  exit 0
}

main "$@"
