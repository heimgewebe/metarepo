#!/usr/bin/env bash
set -euo pipefail

RENOVATE_VERSION="42.99.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/runtime-config.cjs"
NPX_BIN="${RENOVATE_NPX_BIN:-/usr/bin/npx}"
DEFAULT_TOOL_PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:${HOME}/.bun/bin:/usr/local/bin:/usr/bin:/bin"
export PATH="${RENOVATE_TOOL_PATH:-${DEFAULT_TOOL_PATH}}"

RUNTIME_DIR="${RENOVATE_XDG_RUNTIME_DIR:-${XDG_RUNTIME_DIR:-/run/user/$(id -u)}}"
if [[ -d "${RUNTIME_DIR}" ]]; then
  export XDG_RUNTIME_DIR="${RUNTIME_DIR}"
  export DBUS_SESSION_BUS_ADDRESS="unix:path=${RUNTIME_DIR}/bus"
fi

# Renovate runs in fresh clones. Host-wide hooks are workstation policy for
# interactive checkouts and must not interfere with the bot's own branch
# lifecycle, especially remote branch cleanup.
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=core.hooksPath
export GIT_CONFIG_VALUE_0=/dev/null

[[ "${NPX_BIN}" == /* && -x "${NPX_BIN}" ]] || {
  echo "RENOVATE_NPX_BIN must name an executable absolute path: ${NPX_BIN}" >&2
  exit 2
}
command -v gh > /dev/null 2>&1 || {
  echo "gh is required" >&2
  exit 2
}
[[ -f "${CONFIG_FILE}" ]] || {
  echo "Renovate runtime config missing: ${CONFIG_FILE}" >&2
  exit 2
}

TOKEN="$(gh auth token)"
[[ -n "${TOKEN}" ]] || {
  echo "gh auth token returned an empty token" >&2
  exit 2
}

export RENOVATE_TOKEN="${TOKEN}"
export RENOVATE_CONFIG_FILE="${CONFIG_FILE}"
unset TOKEN

exec "${NPX_BIN}" --yes "renovate@${RENOVATE_VERSION}" "$@"
