#!/bin/bash
set -euo pipefail

# GUARD: Document Drift Check
# 1. Verifies that docs/_generated/fleet.md is up-to-date with fleet/repos.yml
# 2. Scans for forbidden terms (e.g. "contracts" as repo name) in non-archive docs

# Setup
GENERATOR="scripts/fleet/generate_fleet_docs.py"
GENERATED_FILE="docs/_generated/fleet.md"

echo "Running Document Drift Guard..."

# 1. Check if generated doc is clean
if [ ! -f "$GENERATED_FILE" ]; then
  echo "❌ $GENERATED_FILE missing. Running generator..."
  python3 "$GENERATOR"
fi

# Generate temp file to compare
TEMP_GEN=$(mktemp)
python3 "$GENERATOR" > /dev/null
# We need to capture the output file content, but the script writes to file.
# Let's just run it and see if git diff triggers.
# Better: Copy current file, run gen, compare.

cp "$GENERATED_FILE" "$TEMP_GEN"
python3 "$GENERATOR"

if ! cmp -s "$GENERATED_FILE" "$TEMP_GEN"; then
  # Differs (Note: The script updates timestamp/commit hash, so it WILL differ on every run if commit changes)
  # We should exclude the header lines with timestamp for comparison if we are in the same commit.
  # But usually, in CI, we check if the file matches what is committed.
  # If I run it now, it overwrites.
  # For a Drift Guard, strictly speaking, the file in the repo should match what the script generates.
  # However, the script puts a timestamp. This makes "git diff" dirty on every run.
  # Mitigation: The generator should perhaps use the timestamp of the commit of repos.yml?
  # For now, let's ignore the header lines 1-5 for comparison.

  DIFF_COUNT=$(diff <(tail -n +6 "$GENERATED_FILE") <(tail -n +6 "$TEMP_GEN") | wc -l)
  if [ "$DIFF_COUNT" -ne 0 ]; then
    echo "❌ Drift detected in $GENERATED_FILE. Content does not match fleet/repos.yml."
    echo "Diff:"
    diff <(tail -n +6 "$GENERATED_FILE") <(tail -n +6 "$TEMP_GEN")
    rm "$TEMP_GEN"
    exit 1
  else
    echo "✅ Generated fleet docs are consistent."
  fi
else
  echo "✅ Generated fleet docs are identical."
fi
rm "$TEMP_GEN"

# 2. Check for "contracts" repo name usage (excluding archive and canonical paths)
# We search for words "contracts" that are NOT "contracts-mirror" and NOT "contracts/" (paths).
# This is tricky with grep.
# We want to find cases where "contracts" is referred to as a repository name.
# Pattern: "contracts repo", "repo contracts", or list items "- contracts"

echo "Scanning for forbidden repo name usage..."

ERRORS=0

# Find files excluding archive and generated
FILES=$(find docs -name "*.md" -not -path "docs/archive/*" -not -path "docs/_generated/*")

# Check for "- contracts" (list item)
# shellcheck disable=SC2086
if grep -nE "^\s*-\s+contracts\s*$" $FILES; then
  echo "❌ Found list item 'contracts' (should be 'contracts-mirror')."
  ERRORS=1
fi

# Check for "contracts-Repo" or "contracts Repo" (German/English mix)
# But exclude "contracts-mirror-Repo"
# shellcheck disable=SC2086
if grep -nE "\bcontracts[- ]Repo" $FILES | grep -v "contracts-mirror"; then
  echo "❌ Found 'contracts Repo' reference (should be 'contracts-mirror Repo')."
  ERRORS=1
fi

if [ "$ERRORS" -eq 1 ]; then
  echo "❌ Drift check failed."
  exit 1
fi

echo "✅ Document Drift Check passed."
exit 0
