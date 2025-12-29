#!/usr/bin/env bash
set -euo pipefail

# Scripts to validate toolchain.versions.yml
# 1. Checks YAML syntax
# 2. Converts to JSON
# 3. Validates JSON against schema

REPO_ROOT="$(git rev-parse --show-toplevel)"
TOOLCHAIN_FILE="${REPO_ROOT}/toolchain.versions.yml"
SCHEMA_FILE="${REPO_ROOT}/.github/schemas/toolchain.versions.schema.json"
JSON_TMP="/tmp/toolchain.versions.json"

# Ensure yq is available
if ! command -v yq >/dev/null 2>&1; then
  if [ -f "${REPO_ROOT}/tools/bin/yq" ]; then
    export PATH="${REPO_ROOT}/tools/bin:$PATH"
  else
    echo "::error::yq not found. Please install it first."
    exit 1
  fi
fi

echo "Validating toolchain.versions.yml..."

# 1. YAML Syntax Check
echo "  [1/3] Checking YAML syntax..."
if ! yq eval '.' "$TOOLCHAIN_FILE" >/dev/null; then
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

if [ ! -f "$SCHEMA_FILE" ]; then
  echo "::error::Schema file not found at $SCHEMA_FILE"
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "::warning::npx not found, skipping schema validation."
  exit 0
fi

# Use npx to run ajv-cli
if ! npx --yes ajv-cli@5 validate -s "$SCHEMA_FILE" -d "$JSON_TMP" --all-errors; then
  echo "::error::Schema validation failed."
  exit 1
fi

echo "  OK. Toolchain configuration is valid."
