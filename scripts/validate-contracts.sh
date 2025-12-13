#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d contracts ]]; then
  echo "contracts directory not found – nothing to validate"
  exit 0
fi
if ! command -v npm > /dev/null 2>&1; then
  echo "::error::npm is required to validate contracts"
  exit 1
fi
# Prefer npx to avoid global state on shared runners
shopt -s nullglob globstar
schemas=(contracts/**/*.schema.json)
if ((${#schemas[@]} == 0)); then
  echo "::notice::No schemas found under contracts/"
else
  for schema in "${schemas[@]}"; do
    echo "::group::Schema ${schema}"
    npx --yes -p ajv-cli@5 -p ajv-formats ajv compile -s "${schema}" --strict=log --spec=draft2020 -c ajv-formats
    echo "::endgroup::"
  done
fi

# Validate examples
examples=(contracts/examples/*.example.json)
if ((${#examples[@]} == 0)); then
  echo "::notice::No examples found under contracts/examples/"
else
  for example in "${examples[@]}"; do
    filename=$(basename "$example" .example.json)
    schema="contracts/${filename}.schema.json"

    echo "::group::Validate Example ${example}"
    if [[ -f "$schema" ]]; then
      npx --yes -p ajv-cli@5 -p ajv-formats ajv validate -s "$schema" -d "$example" --strict=false -c ajv-formats --spec=draft2020
    else
      echo "::notice::No matching schema found for $example (expected $schema)"
    fi
    echo "::endgroup::"
  done
fi

# Fixtures check: use nullglob/globstar from above
fixtures=(fixtures/**/*.jsonl)
if ((${#fixtures[@]} > 0)); then
  for fixture in "${fixtures[@]}"; do
    base="$(basename "${fixture}" .jsonl)"
    schema="contracts/${base}.schema.json"
    echo "::group::Validate ${fixture}"
    if [[ -f "${schema}" ]]; then
      npx --yes -p ajv-cli@5 -p ajv-formats ajv validate -s "${schema}" -d "${fixture}" --spec=draft2020 --errors=line --all-errors -c ajv-formats --strict=log
    else
      echo "::notice::No matching schema for ${fixture} (expected ${schema})"
    fi
    echo "::endgroup::"
  done
else
  echo "No fixtures found under fixtures/"
fi
