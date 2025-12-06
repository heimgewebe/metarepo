#!/usr/bin/env bash
set -euo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root"

index_file="docs/contracts-index.md"

if [[ ! -f "$index_file" ]]; then
  echo "::error::Contracts-Index $index_file fehlt."
  exit 1
fi

missing=0

shopt -s nullglob
for f in contracts/*.schema.json; do
  bn=$(basename "$f")
  if ! grep -q "\`$bn\`" "$index_file"; then
    echo "::error file=$index_file::Contract-Datei $bn ist nicht im Contracts-Index referenziert."
    missing=1
  fi
done

# Optional: YAML-Contracts mitprüfen (als Warning, nicht Error)
for f in contracts/*.yml contracts/*.yaml; do
  [[ -e "$f" ]] || continue
  bn=$(basename "$f")
  if ! grep -q "\`$bn\`" "$index_file"; then
    echo "::warning file=$index_file::YAML-Contract $bn ist nicht im Contracts-Index referenziert."
  fi
done

if [[ $missing -eq 0 ]]; then
  echo "✓ Alle zentralen Contracts sind im Index referenziert."
fi

exit $missing
