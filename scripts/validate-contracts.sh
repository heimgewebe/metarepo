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
shopt -s nullglob globstar 2> /dev/null || true

# Check if globstar is actually active (Bash 4+)
globstar_ok=0
shopt -q globstar 2> /dev/null && globstar_ok=1

if [[ "$globstar_ok" -eq 1 ]]; then
  schemas=(contracts/**/*.schema.json)
else
  # Bash 3 fallback
  schemas=()
  while IFS= read -r s; do
    schemas+=("$s")
  done < <(find contracts -type f -name "*.schema.json" -print 2> /dev/null)
fi

if ((${#schemas[@]} == 0)); then
  echo "::notice::No schemas found under contracts/"
else
  for schema in "${schemas[@]}"; do
    echo "::group::Schema ${schema}"

    # Build a list of references excluding the current schema to avoid duplicate ID errors
    refs=()
    for s in "${schemas[@]}"; do
      if [[ "$s" != "$schema" ]]; then
        refs+=("$s")
      fi
    done

    # AJV CLI allows multiple -r arguments
    # We pass all other schemas as references

    # Construct args array
    args=("--strict=log" "--spec=draft2020" "-c" "ajv-formats" "-s" "${schema}")
    for r in "${refs[@]}"; do
      args+=("-r" "$r")
    done

    npx --yes -p ajv-cli@5 -p ajv-formats ajv compile "${args[@]}"
    echo "::endgroup::"
  done
fi

# Validate examples
if [[ "$globstar_ok" -eq 1 ]]; then
  examples=(contracts/examples/**/*.example.json)
else
  examples=()
  while IFS= read -r e; do
    examples+=("$e")
  done < <(find contracts/examples -type f -name "*.example.json" -print 2> /dev/null)
fi

if ((${#examples[@]} == 0)); then
  echo "::notice::No examples found under contracts/examples/"
else
  for example in "${examples[@]}"; do
    filename=$(basename "$example" .example.json)

    # Calculate relative dir from contracts/examples
    # e.g., contracts/examples/webmaschine/state/foo.example.json -> webmaschine/state
    example_dir=$(dirname "$example")
    # Using python to get relative path is robust but let's try pure bash text processing
    # Remove prefix contracts/examples/ or contracts/examples
    rel_dir=${example_dir#contracts/examples}
    rel_dir=${rel_dir#/}

    # Search for candidates recursively
    candidates=()
    if [[ "$globstar_ok" -eq 1 ]]; then
      # Bash 4+ recursive glob
      candidates=(contracts/**/"${filename}.schema.json")
    else
      # Bash 3 fallback using find
      while IFS= read -r c; do
        candidates+=("$c")
      done < <(find contracts -type f -name "${filename}.schema.json" -print 2> /dev/null)
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

    # Disambiguation logic
    final_candidate=""
    if ((${#found[@]} == 1)); then
      final_candidate="${found[0]}"
    elif ((${#found[@]} > 1)); then
      # Try to match directory structure
      matched_candidates=()
      for c in "${found[@]}"; do
        c_dir=$(dirname "$c")
        # Check if c_dir ends with rel_dir
        if [[ -z "$rel_dir" ]]; then
          # If rel_dir is empty (root example), prefer root schema or 'contracts/events' (historical)
          # We check if schema is in root 'contracts' or direct subfolder 'contracts/events'
          # Simple heuristic: shorter path wins for root examples
          matched_candidates+=("$c")
        else
          # Check if path contains rel_dir
          if [[ "$c_dir" == *"$rel_dir" ]]; then
            matched_candidates+=("$c")
          fi
        fi
      done

      # If filtering helped, update found list
      if ((${#matched_candidates[@]} > 0)); then
        found=("${matched_candidates[@]}")
      fi

      # If still multiple, pick shortest path
      if ((${#found[@]} == 1)); then
        final_candidate="${found[0]}"
      else
        # Sort by length
        sorted=$(printf '%s\n' "${found[@]}" | awk '{ print length, $0 }' | sort -n | cut -d" " -f2-)
        # Pick first
        final_candidate=$(echo "$sorted" | head -n1)
      fi
    fi

    echo "::group::Validate Example ${example}"
    if [[ -n "$final_candidate" ]]; then
      schema="$final_candidate"

      # Build reference args excluding current schema to be safe (though validate -s overrides -r usually)
      # Actually for validation, we want ALL schemas as refs, including others.
      # AJV might complain if -s and -r have same ID. Safe bet is to exclude.
      refs=()
      for s in "${schemas[@]}"; do
        if [[ "$s" != "$schema" ]]; then
          refs+=("$s")
        fi
      done

      args=("--strict=false" "--spec=draft2020" "-c" "ajv-formats" "-s" "${schema}" "-d" "${example}")
      for r in "${refs[@]}"; do
        args+=("-r" "$r")
      done

      npx --yes -p ajv-cli@5 -p ajv-formats ajv validate "${args[@]}"
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
      done < <(find contracts -type f -name "${base}.schema.json" -print 2> /dev/null)
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

      # Build reference args
      refs=()
      for s in "${schemas[@]}"; do
        if [[ "$s" != "$schema" ]]; then
          refs+=("$s")
        fi
      done

      args=("--strict=log" "--spec=draft2020" "-c" "ajv-formats" "--errors=line" "--all-errors" "-s" "${schema}" "-d" "${fixture}")
      for r in "${refs[@]}"; do
        args+=("-r" "$r")
      done

      npx --yes -p ajv-cli@5 -p ajv-formats ajv validate "${args[@]}"
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
