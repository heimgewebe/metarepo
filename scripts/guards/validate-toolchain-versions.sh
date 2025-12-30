#!/usr/bin/env bash
set -euo pipefail

# GUARD: validate-toolchain-versions.sh
# Ensures toolchain.versions.yml complies with the canonical schema.
# Pre-requisite: yq and ajv (via npx or global) must be available.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLCHAIN_FILE="${ROOT_DIR}/toolchain.versions.yml"
SCHEMA_FILE="${ROOT_DIR}/contracts/tooling/toolchain.versions.schema.json"

log() { echo "::notice::$*" >&2; }
err() { echo "::error::$*" >&2; }

if [[ ! -f "${TOOLCHAIN_FILE}" ]]; then
  err "toolchain.versions.yml not found at ${TOOLCHAIN_FILE}"
  exit 1
fi

if [[ ! -f "${SCHEMA_FILE}" ]]; then
  err "Schema not found at ${SCHEMA_FILE}"
  exit 1
fi

# Ensure yq is available (should be bootstrapped by setup-yq)
if ! command -v yq >/dev/null 2>&1; then
  err "yq command not found. Cannot convert YAML to JSON for validation."
  exit 1
fi

# Agent-Mode handling for ajv
if [[ "${AGENT_MODE:-}" != "" ]]; then
  if ! command -v ajv >/dev/null 2>&1; then
    err "ajv-cli not found in Agent-Mode. Please pre-install it or disable Agent-Mode."
    exit 1
  fi
  # Use local ajv
  CMD="ajv"
else
  # Use npx wrapper if not in agent mode
  CMD="npx --yes ajv-cli@5.0.0"
fi

log "Validating ${TOOLCHAIN_FILE} against schema..."

# Convert YAML to JSON and pipe to ajv
# Using a temporary file for JSON to ensure clean validation context
# Note: ajv-cli requires .json extension to properly detect the file format
# Use portable mktemp syntax (macOS doesn't support --suffix)
TMP_JSON="$(mktemp "${TMPDIR:-/tmp}/toolchain.XXXXXXXXXX.json")"
trap 'rm -f "${TMP_JSON}"' EXIT

yq -o=json '.' "${TOOLCHAIN_FILE}" > "${TMP_JSON}"

if $CMD validate --spec=draft2020 --strict=log -s "${SCHEMA_FILE}" -d "${TMP_JSON}"; then
  echo "✅ toolchain.versions.yml is valid."
else
  err "toolchain.versions.yml validation failed."
  exit 1
fi
