#!/usr/bin/env bash
set -euo pipefail

RENOVATE_VERSION="42.99.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/runtime-config.cjs"

command -v gh > /dev/null 2>&1 || {
  echo "gh is required" >&2
  exit 2
}
command -v npx > /dev/null 2>&1 || {
  echo "npx is required" >&2
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

exec npx --yes "renovate@${RENOVATE_VERSION}" "$@"
