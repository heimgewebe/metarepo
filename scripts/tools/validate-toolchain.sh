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
JSON_TMP="$(mktemp -t toolchain.versions.XXXXXX.json)"
trap 'rm -f "$JSON_TMP"' EXIT

# Robust existence checks
test -f "$TOOLCHAIN_FILE" || { echo "::error::Missing toolchain file: $TOOLCHAIN_FILE"; exit 1; }
test -f "$SCHEMA_FILE" || { echo "::error::Missing schema file: $SCHEMA_FILE"; exit 1; }

# Ensure yq is available and prioritize repo-local version
if [ -f "${REPO_ROOT}/tools/bin/yq" ]; then
  export PATH="${REPO_ROOT}/tools/bin:$PATH"
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "::error::yq not found. Please install it first."
  exit 1
fi

# Verify yq version/flavor
YQ_PATH="$(command -v yq)"
YQ_VER="$(yq --version 2>&1 || true)"
echo "Using yq: $YQ_PATH ($YQ_VER)"

if ! echo "$YQ_VER" | grep -q "version v4\."; then
  echo "::error::Wrong yq version/flavor detected. Expected mikefarah/yq v4.x"
  exit 1
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

if ! command -v npx >/dev/null 2>&1; then
  echo "::error::npx missing (node setup broken), cannot run schema validation."
  exit 1
fi

# Use npx to run ajv-cli
if ! npx --yes ajv-cli@5 validate -s "$SCHEMA_FILE" -d "$JSON_TMP" --all-errors; then
  echo "::error::Schema validation failed."
  exit 1
fi

echo "  OK. Toolchain configuration is valid."
