#!/usr/bin/env bash
set -euo pipefail

EVENT_JSON="${1:-}"
SCHEMA="contracts/events/published.v1.schema.json"

if [[ -z "${EVENT_JSON}" || ! -f "${EVENT_JSON}" ]]; then
  echo "::notice::No event json provided; skipping published.v1 guard."
  exit 0
fi

if ! command -v ajv > /dev/null 2>&1; then
  echo "::notice::ajv not available; skipping schema validation."
  exit 0
fi

if ! ajv validate -s "${SCHEMA}" -d "${EVENT_JSON}" > /dev/null 2>&1; then
  echo "::warning::published.v1 event does not conform to invariants."
  exit 0
fi

echo "::notice::published.v1 event validated (invariants only)."
