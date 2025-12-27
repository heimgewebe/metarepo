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
shopt -s nullglob globstar || true
# Note: globstar is Bash 4+, but we attempt to use it.
# If running on Bash 3 (macOS), this might fail to expand recursively.
# For strict Bash 3 compatibility, 'find' would be needed, but this script
# primarily targets CI (Bash 4+). The logic below avoids mapfile for better portability.

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

    # Search for candidates recursively
    candidates=(contracts/**/"${filename}.schema.json")

    # Deduplicate candidates (portable, works on Bash < 4 if tools present)
    # 1. Print candidates (newline separated)
    # 2. Sort unique
    # 3. Read back into array using while-read loop (avoids mapfile)
    unique_candidates=()
    while IFS= read -r line; do
      [[ -n "$line" ]] && unique_candidates+=("$line")
    done < <(printf '%s\n' "${candidates[@]}" | sort -u)

    # Filter for existing files (sanity check)
    found=()
    for c in "${unique_candidates[@]}"; do
      [[ -f "$c" ]] && found+=("$c")
    done

    echo "::group::Validate Example ${example}"
    if ((${#found[@]} == 1)); then
      schema="${found[0]}"
      # Check if schema references base.event.schema.json (broad check)
      if grep -q "base\.event\.schema\.json" "$schema" 2>/dev/null; then
        ref_schema="contracts/events/base.event.schema.json"
        if [[ -f "$ref_schema" ]]; then
           npx --yes -p ajv-cli@5 -p ajv-formats ajv validate \
            -s "$schema" \
            -r "$ref_schema" \
            -d "$example" \
            --strict=false -c ajv-formats --spec=draft2020
        else
            echo "::error::Schema $schema references base.event.schema.json, but it was not found at $ref_schema"
            exit 2
        fi
      else
        npx --yes -p ajv-cli@5 -p ajv-formats ajv validate \
          -s "$schema" -d "$example" --strict=false -c ajv-formats --spec=draft2020
      fi
    elif ((${#found[@]} > 1)); then
      echo "::error::Ambiguous schema match for $example. Found multiple candidates:"
      printf '  - %s\n' "${found[@]}"
      exit 2
    else
      echo "::notice::No matching schema found for $example (searched contracts/**/${filename}.schema.json)"
    fi
    echo "::endgroup::"
  done
fi

# Fixtures check: use nullglob/globstar from above
fixtures=(fixtures/**/*.jsonl)
if ((${#fixtures[@]} > 0)); then
  for fixture in "${fixtures[@]}"; do
    base="$(basename "${fixture}" .jsonl)"

    # Search for candidates recursively
    candidates=(contracts/**/"${base}.schema.json")

    # Deduplicate candidates (portable)
    unique_candidates=()
    while IFS= read -r line; do
       [[ -n "$line" ]] && unique_candidates+=("$line")
    done < <(printf '%s\n' "${candidates[@]}" | sort -u)

    # Filter for existing files
    found=()
    for c in "${unique_candidates[@]}"; do
      [[ -f "$c" ]] && found+=("$c")
    done

    echo "::group::Validate ${fixture}"
    if ((${#found[@]} == 1)); then
      schema="${found[0]}"
      npx --yes -p ajv-cli@5 -p ajv-formats ajv validate -s "${schema}" -d "${fixture}" --spec=draft2020 --errors=line --all-errors -c ajv-formats --strict=log
    elif ((${#found[@]} > 1)); then
      echo "::error::Ambiguous schema match for ${fixture}. Found multiple candidates:"
      printf '  - %s\n' "${found[@]}"
      exit 2
    else
      echo "::notice::No matching schema for ${fixture} (searched contracts/**/${base}.schema.json)"
    fi
    echo "::endgroup::"
  done
else
  echo "No fixtures found under fixtures/"
fi
