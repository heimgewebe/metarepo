#!/bin/bash
set -euo pipefail

# Script to check for drift in generated integrity sources.
# Returns exit code 1 if drift is detected (generated file differs from committed file).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="${REPO_ROOT}/scripts/generate_integrity_sources.py"
OUTPUT_FILE="${REPO_ROOT}/reports/integrity/sources.v1.json"

echo "Checking for drift in integrity sources..."

if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Error: $OUTPUT_FILE is missing. Generate and commit it before running the drift check."
  exit 1
fi

CANDIDATE=$(mktemp)

# Invoked indirectly by the EXIT trap below.
# shellcheck disable=SC2317
cleanup_candidate() {
  rc=$?
  trap - EXIT
  if ! rm -f "$CANDIDATE"; then
    echo "Error: Failed to remove temporary integrity candidate." >&2
    rc=1
  fi
  exit "$rc"
}

trap cleanup_candidate EXIT

# Generate a candidate without ever rewriting the tracked report.
CMD=("python3")
if command -v uv > /dev/null 2>&1; then
  CMD=("uv" "run" "--" "python3")
fi

set +e
"${CMD[@]}" "$SCRIPT_PATH" --output "$CANDIDATE"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  echo "Error: Generator script failed."
  exit "$rc"
fi

if ! cmp -s "$OUTPUT_FILE" "$CANDIDATE"; then
  echo "Error: Drift detected in $OUTPUT_FILE."
  echo "Diff (committed/current -> generated):"
  diff -u "$OUTPUT_FILE" "$CANDIDATE" || true
  echo "Please run 'python3 scripts/generate_integrity_sources.py' and commit the changes."
  exit 1
fi

echo "Success: No drift detected."
exit 0
