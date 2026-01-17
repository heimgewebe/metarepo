#!/bin/bash
set -euo pipefail

# Script to check for drift in generated integrity sources.
# Returns exit code 1 if drift is detected (generated file differs from committed file).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="${REPO_ROOT}/scripts/generate_integrity_sources.py"
OUTPUT_FILE="${REPO_ROOT}/reports/integrity/sources.v1.json"

echo "Checking for drift in integrity sources..."

# Run the generator
CMD="python3"
if command -v uv >/dev/null 2>&1; then
    CMD="uv run -- python3"
fi

if ! $CMD "$SCRIPT_PATH"; then
  echo "Error: Generator script failed."
  exit 1
fi

# Check for diffs
if ! git diff --exit-code "$OUTPUT_FILE"; then
  echo "Error: Drift detected in $OUTPUT_FILE."
  echo "Please run 'python3 scripts/generate_integrity_sources.py' and commit the changes."
  exit 1
fi

echo "Success: No drift detected."
exit 0
