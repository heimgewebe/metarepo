#!/usr/bin/env bash
set -euo pipefail
file="${1:-}"
[[ -f "$file" ]] || { echo "usage: $0 .agents/runs/<id>.jsonl" >&2; exit 2; }
jq -r '[.ts,.type, ( .payload.id // "-" ), ( .payload.rc // "" )] | @tsv' "$file" \
 | column -t -s$'\t'
