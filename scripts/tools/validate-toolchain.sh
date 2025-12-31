#!/usr/bin/env bash
set -euo pipefail

# Scripts to validate toolchain.versions.yml
# 1. Checks YAML syntax
# 2. Checks for empty/null values
# 3. Converts to JSON
# 4. Validates JSON against schema

REPO_ROOT="${GITHUB_WORKSPACE:-$(git rev-parse --show-toplevel)}"
TOOLCHAIN_FILE="${REPO_ROOT}/toolchain.versions.yml"
SCHEMA_FILE="${REPO_ROOT}/.github/schemas/toolchain.versions.schema.json"
# Note: ajv-cli requires .json extension to properly detect the file format
# Use portable mktemp syntax (macOS doesn't support --suffix)
JSON_TMP="$(mktemp "${TMPDIR:-/tmp}/toolchain.XXXXXXXXXX.json")"
trap 'rm -f "$JSON_TMP"' EXIT

# Robust existence checks
test -f "$TOOLCHAIN_FILE" || {
  echo "::error::Missing toolchain file: $TOOLCHAIN_FILE"
  exit 1
}
test -f "$SCHEMA_FILE" || {
  echo "::error::Missing schema file: $SCHEMA_FILE"
  exit 1
}

# Ensure yq is available and is the correct one (mikefarah/yq with eval support)
# This prevents the "invalid YAML" phantom when python-yq or no yq is in PATH.
if ! command -v yq > /dev/null 2>&1 || ! yq eval --help > /dev/null 2>&1; then
  echo "::notice::yq missing or incompatible (need mikefarah/yq v4 with eval). Bootstrapping..."

  # Try local tools/bin first
  if [ -f "${REPO_ROOT}/tools/bin/yq" ] && "${REPO_ROOT}/tools/bin/yq" eval --help > /dev/null 2>&1; then
    export PATH="${REPO_ROOT}/tools/bin:$PATH"
    echo "::notice::Using local yq from tools/bin"
  else
    # Bootstrap via yq-pin.sh
    if [ -x "${REPO_ROOT}/scripts/tools/yq-pin.sh" ]; then
      echo "::notice::Running yq-pin.sh to install correct yq..."
      "${REPO_ROOT}/scripts/tools/yq-pin.sh" ensure
      export PATH="${REPO_ROOT}/tools/bin:$PATH"
    else
      echo "::error::yq not found and cannot bootstrap (yq-pin.sh missing or not executable)."
      exit 1
    fi
  fi
fi

# Diagnostic: log yq version for troubleshooting
if command -v yq > /dev/null 2>&1; then
  yq_version="$(yq --version 2>&1 || echo 'unknown')"
  echo "::notice::Using yq version: ${yq_version}"
else
  echo "::error::yq still not available after bootstrap attempt."
  exit 1
fi

echo "Validating toolchain.versions.yml..."

# 1. YAML Syntax Check
echo "  [1/3] Checking YAML syntax..."
if ! yq eval '.' "$TOOLCHAIN_FILE" > /dev/null; then
  echo "::error::${TOOLCHAIN_FILE} contains invalid YAML syntax."
  exit 1
fi
echo "  OK."

# 2. Convert to JSON
echo "  [2/3] Converting to JSON..."
yq eval -o=json '.' "$TOOLCHAIN_FILE" > "$JSON_TMP"
echo "  OK."

# 3. JSON Schema Validation
echo "  [3/3] Validating against schema..."

# Check for Node/npx availability
if ! command -v npx > /dev/null 2>&1; then
  echo "::warning::npx not available. Skipping JSON schema validation. To enable full validation, ensure Node.js is installed."
  echo "  Schema validation skipped (npx unavailable)."
  exit 0
fi

# Use npx to run ajv-cli
if ! npx --yes ajv-cli@5 validate -s "$SCHEMA_FILE" -d "$JSON_TMP" --all-errors; then
  echo "::error::Schema validation failed."
  exit 1
fi

echo "  OK. Toolchain configuration is valid."
