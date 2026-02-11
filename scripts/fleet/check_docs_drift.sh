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

# Optional dependency: prefer ripgrep when available, but keep guard portable.
has_rg() {
  command -v rg > /dev/null 2>&1
}

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

# 3. Guard against stale repo-identity references to legacy repo name "tools"
# Allowlist rules:
# - reports/sync-logs/** may contain historical names by design.
# - tools/** is a local toolchain tree, not repo identity.
# - scripts/tools/** contains local helper scripts, not repo identity.
# Note: docs/archive/** was migrated (tools→lenskit) in commit 7038fdd, so no exclusion needed.

echo "Scanning for stale repo-identity references (tools -> lenskit)..."

LEGACY_PATTERN_PCRE='(github\.com/heimgewebe/tools|heimgewebe/tools|^\s*-\s*name:\s*tools\s*$|ALLOWED_TARGET_REPOS:.*\btools\b)'
LEGACY_PATTERN_ERE='(github\.com/heimgewebe/tools|heimgewebe/tools|^[[:space:]]*-[[:space:]]*name:[[:space:]]*tools[[:space:]]*$|ALLOWED_TARGET_REPOS:.*(^|[^[:alnum:]_])tools([^[:alnum:]_]|$))'
if has_rg; then
  set +e
  rg -n --pcre2 \
    --glob '!reports/sync-logs/**' \
    --glob '!tools/**' \
    --glob '!scripts/tools/**' \
    --glob '!scripts/fleet/check_docs_drift.sh' \
    "$LEGACY_PATTERN_PCRE" .
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    echo "❌ Found stale repo-identity reference(s) to 'tools'. Use 'lenskit' instead."
    exit 1
  elif [ "$rc" -eq 1 ]; then
    :
  else
    echo "❌ rg failed (exit=$rc). Guard cannot be trusted. Failing hard."
    exit 1
  fi
else
  echo "⚠️  rg not found; falling back to grep -r with ERE mode."
  set +e
  GREP_OUT=$(
    grep -r -I -n -E \
      --exclude-dir='.git' \
      --exclude-dir='reports' \
      --exclude-dir='tools' \
      --exclude='check_docs_drift.sh' \
      -e "$LEGACY_PATTERN_ERE" \
      . \
      2>&1
  )
  rc=$?
  set -e

  if [ "$rc" -eq 0 ]; then
    # Matches found
    echo "$GREP_OUT"
    echo "❌ Found stale repo-identity reference(s) to 'tools'. Use 'lenskit' instead."
    exit 1
  elif [ "$rc" -eq 1 ]; then
    # No matches - clean
    :
  else
    # grep error (exit 2+)
    if [ -n "$GREP_OUT" ]; then
      echo "$GREP_OUT" >&2
    fi
    echo "❌ grep failed (exit=$rc). Guard cannot be trusted. Failing hard." >&2
    exit 1
  fi
fi

echo "✅ Legacy repo-identity guard passed."

echo "✅ Document Drift Check passed."
exit 0
