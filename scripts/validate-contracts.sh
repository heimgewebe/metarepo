#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

if [[ ! -d contracts ]]; then
  echo "contracts directory not found – nothing to validate"
  exit 0
fi
if ! command -v npm > /dev/null 2>&1; then
  echo "::error::npm is required to validate contracts"
  exit 1
fi
if ! command -v node > /dev/null 2>&1; then
  echo "::error::node is required to validate contracts"
  exit 1
fi

if ! command -v python3 > /dev/null 2>&1; then
  echo "::error::python3 is required to strictly parse contract JSON"
  exit 1
fi
python3 scripts/check-contract-json.py contracts

# --- Setup direct AJV runtime ---
echo "::group::Setup Validator"
# Robust mktemp for Linux/macOS/BSD
TMP_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t 'ajv')
trap 'rm -rf "$TMP_DIR"' EXIT

AJV_VERSION=8.20.0
AJV_FORMATS_VERSION=3.0.1
AJV_MODULES="$TMP_DIR/node_modules"
AJV_RUNNER="$ROOT_DIR/scripts/contracts/ajv_validate.cjs"
AJV_PACKAGE_JSON="$ROOT_DIR/contracts/package.json"
AJV_PACKAGE_LOCK="$ROOT_DIR/contracts/package-lock.json"

for validator_input in "$AJV_RUNNER" "$AJV_PACKAGE_JSON" "$AJV_PACKAGE_LOCK"; do
  if [[ ! -f "$validator_input" ]]; then
    echo "::error::Required validator input not found at $validator_input"
    exit 1
  fi
done

echo "Installing lock-bound AJV runtime..."
cp "$AJV_PACKAGE_JSON" "$TMP_DIR/package.json"
cp "$AJV_PACKAGE_LOCK" "$TMP_DIR/package-lock.json"
# --loglevel error suppresses warnings but keeps errors
# --ignore-scripts prevents execution of malicious/unnecessary lifecycle scripts
# --no-fund hides funding messages
if ! npm ci --prefix "$TMP_DIR" --no-audit --ignore-scripts --no-fund --loglevel error; then
  echo "::error::Failed to install lock-bound AJV runtime"
  exit 1
fi

actual_ajv=$(node -p 'require(process.argv[1]).version' "$AJV_MODULES/ajv/package.json")
actual_formats=$(node -p 'require(process.argv[1]).version' "$AJV_MODULES/ajv-formats/package.json")
if [[ "$actual_ajv" != "$AJV_VERSION" || "$actual_formats" != "$AJV_FORMATS_VERSION" ]]; then
  echo "::error::Installed AJV runtime does not match pinned versions"
  echo "Expected ajv=$AJV_VERSION ajv-formats=$AJV_FORMATS_VERSION"
  echo "Found ajv=$actual_ajv ajv-formats=$actual_formats"
  exit 1
fi

echo "Direct validator ready: ajv=$actual_ajv ajv-formats=$actual_formats"
echo "::endgroup::"
# ----------------------------------

shopt -s nullglob globstar 2> /dev/null || true

# Check if globstar is actually active (Bash 4+)
globstar_ok=0
shopt -q globstar 2> /dev/null && globstar_ok=1

if [[ "$globstar_ok" -eq 1 ]]; then
  # We intentionally exclude examples from being treated as schemas
  # Using find is safer for complex exclusion than extglob
  # contracts/**/*.schema.json might pick up contracts/examples/foo.schema.json if we are not careful
  # So we use find consistently for collection, ensuring deterministic sort
  schemas=()
  while IFS= read -r s; do
    schemas+=("$s")
  done < <(find contracts -path contracts/examples -prune -o -type f -name "*.schema.json" -print | sort)
else
  # Bash 3 fallback
  schemas=()
  while IFS= read -r s; do
    schemas+=("$s")
  done < <(find contracts -path contracts/examples -prune -o -type f -name "*.schema.json" -print | sort)
fi

if ((${#schemas[@]} == 0)); then
  echo "::notice::No schemas found under contracts/"
else
  # Check for duplicate $ids before validation
  echo "::group::Check for Duplicate IDs"
  # Extract IDs and check for duplicates
  # We use grep to find lines with "$id", then sed to extract the value between quotes.
  # Assumes format: "$id": "VALUE",
  # shellcheck disable=SC2016
  duplicates=$(grep -r '"$id"' contracts |
    grep -v "contracts/examples" |
    sed -n 's/.*"\$id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
    sort |
    uniq -d)

  if [[ -n "$duplicates" ]]; then
    echo "::error::Duplicate \$id found in schemas:"
    echo "$duplicates"
    # Identify files containing the duplicates
    for dup in $duplicates; do
      echo "Files with ID '$dup':"
      grep -r "$dup" contracts | grep -v "contracts/examples" | awk -F: '{print "  - " $1}'
    done
    exit 1
  else
    echo "No duplicate IDs found."
  fi
  echo "::endgroup::"

  for schema in "${schemas[@]}"; do
    echo "::group::Schema ${schema}"

    # Build a list of references excluding the current schema to avoid duplicate ID errors
    refs=()
    for s in "${schemas[@]}"; do
      if [[ "$s" != "$schema" ]]; then
        refs+=("$s")
      fi
    done

    # Construct args array for the direct, pinned AJV runner.
    args=("compile" "--modules" "$AJV_MODULES" "--strict" "log" "--schema" "${schema}")
    for r in "${refs[@]}"; do
      args+=("--ref" "$r")
    done

    if ! output=$(node "$AJV_RUNNER" "${args[@]}" 2>&1); then
      echo "::error::Validation failed for schema: ${schema}"
      echo "Command args: ${args[*]}"
      echo "$output"

      if echo "$output" | grep -q "already exists"; then
        echo "::notice::Hint: This error often indicates a duplicate \$id. Check the 'Check for Duplicate IDs' group output above or verify that the schema is not referencing itself via \$ref with the same ID."
      fi
      exit 1
    fi
    echo "$output"
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
    # e.g., contracts/examples/heim-pc/state/foo.example.json -> heim-pc/state
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
          # Root examples carry no directory evidence, so every same-name
          # schema remains a candidate and ambiguity must be handled below.
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

      if ((${#found[@]} == 1)); then
        final_candidate="${found[0]}"
      else
        echo "::error::Ambiguous schema match for ${example}. Found multiple candidates:"
        printf '  - %s\n' "${found[@]}"
        exit 2
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

      args=("validate" "--modules" "$AJV_MODULES" "--strict" "false" "--schema" "${schema}" "--data" "${example}")
      for r in "${refs[@]}"; do
        args+=("--ref" "$r")
      done

      node "$AJV_RUNNER" "${args[@]}"
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

      args=("validate" "--modules" "$AJV_MODULES" "--strict" "log" "--all-errors" "--schema" "${schema}" "--data" "${fixture}")
      for r in "${refs[@]}"; do
        args+=("--ref" "$r")
      done

      node "$AJV_RUNNER" "${args[@]}"
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

# Governance registry: validate lifecycle, provenance and evidence-bound producer/consumer claims.
echo "::group::Validate contract consumer registry"
if command -v uv > /dev/null 2>&1; then
  uv run python scripts/contracts/validate_consumers.py
else
  python3 scripts/contracts/validate_consumers.py
fi
echo "::endgroup::"
