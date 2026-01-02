#!/usr/bin/env bash
set -euo pipefail

PAYLOAD_FILE="reports/integrity/event_payload.json"

if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "FAIL: $PAYLOAD_FILE not found"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "FAIL: jq is missing"
  exit 1
fi

# Validate forbidden keys (strict schema: only allowed keys permitted)
# We subtract the allowed keys from the actual keys. If anything remains, it's forbidden.
EXTRA_KEYS=$(jq -r 'keys - ["url", "generated_at", "repo", "status"] | .[]' "$PAYLOAD_FILE")
if [[ -n "$EXTRA_KEYS" ]]; then
  echo "FAIL: Forbidden keys found: $EXTRA_KEYS"
  exit 1
fi

# Validate mandatory keys
for key in url generated_at repo status; do
  if ! jq -e --arg k "$key" 'has($k)' "$PAYLOAD_FILE" >/dev/null 2>&1; then
    echo "FAIL: Missing mandatory key: $key"
    exit 1
  fi
done

# Validate status value
STATUS=$(jq -r '.status' "$PAYLOAD_FILE")
case "$STATUS" in
  OK|WARN|FAIL|MISSING|UNCLEAR)
    ;;
  *)
    echo "FAIL: Invalid status: $STATUS"
    exit 1
    ;;
esac

echo "Integrity Guard: OK"
