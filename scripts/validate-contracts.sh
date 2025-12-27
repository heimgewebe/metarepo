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
shopt -s nullglob globstar 2>/dev/null || true

# Check if globstar is actually active (Bash 4+)
globstar_ok=0
shopt -q globstar 2>/dev/null && globstar_ok=1

if [[ "$globstar_ok" -eq 1 ]]; then
    schemas=(contracts/**/*.schema.json)
else
    # Bash 3 fallback
    schemas=()
    while IFS= read -r s; do
        schemas+=("$s")
    done < <(find contracts -type f -name "*.schema.json" -print 2>/dev/null)
fi

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
    candidates=()
    if [[ "$globstar_ok" -eq 1 ]]; then
        # Bash 4+ recursive glob
        candidates=(contracts/**/"${filename}.schema.json")
    else
        # Bash 3 fallback using find
        while IFS= read -r c; do
            candidates+=("$c")
        done < <(find contracts -type f -name "${filename}.schema.json" -print 2>/dev/null)
    fi

    # Deduplicate candidates (portable)
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
    candidates=()
    if [[ "$globstar_ok" -eq 1 ]]; then
        # Bash 4+ recursive glob
        candidates=(contracts/**/"${base}.schema.json")
    else
        # Bash 3 fallback using find
        while IFS= read -r c; do
            candidates+=("$c")
        done < <(find contracts -type f -name "${base}.schema.json" -print 2>/dev/null)
    fi

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
