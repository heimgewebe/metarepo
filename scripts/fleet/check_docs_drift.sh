#!/bin/bash
set -euo pipefail

# GUARD: Document Drift Check
# 1. Verifies that docs/_generated/fleet.md is up-to-date with fleet/repos.yml
# 2. Scans for forbidden terms (e.g. "contracts" as repo name) in non-archive docs

# Setup
GENERATOR="scripts/fleet/generate_fleet_docs.py"
GENERATED_FILE="docs/_generated/fleet.md"

echo "Running Document Drift Guard..."

# 1. Check if generated doc exactly matches the canonical source.
if [ ! -f "$GENERATED_FILE" ]; then
  echo "❌ $GENERATED_FILE missing. Run $GENERATOR and commit the result."
  exit 1
fi

ORIGINAL=$(mktemp)
trap 'rm -f "$ORIGINAL"' EXIT
cp "$GENERATED_FILE" "$ORIGINAL"

python3 "$GENERATOR" > /dev/null

if ! cmp -s "$GENERATED_FILE" "$ORIGINAL"; then
  echo "❌ Drift detected in $GENERATED_FILE. Content does not match fleet/repos.yml."
  echo "Diff (committed/current -> generated):"
  diff -u "$ORIGINAL" "$GENERATED_FILE" || true
  cp "$ORIGINAL" "$GENERATED_FILE"
  exit 1
fi

echo "✅ Generated fleet docs are identical."

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

# 3. Guard against stale active repo identities "tools" and "lenskit"
# Allowlist rules:
# - reports/sync-logs/** and docs/archive/** are immutable historical evidence.
# - tools/** and scripts/tools/** are local toolchain trees, not repo identity.
# - the command-dispatch workflow intentionally recognizes legacy aliases so it
#   can direct callers to RepoGround; the patterns below target active identity
#   declarations and allowlists, not that explicit compatibility branch.
# - this script contains the guard patterns itself.

echo "Scanning for stale repo identities (tools/lenskit -> repoground)..."

LEGACY_PATTERN_RG='(github\.com/heimgewebe/(tools|lenskit)(\.git)?|heimgewebe/(tools|lenskit)\b|^\s*-\s*name:\s*(tools|lenskit)\s*$|^\s*name:\s*(tools|lenskit)\s*$|ALLOWED_TARGET_REPOS:.*\b(tools|lenskit)\b)'
LEGACY_PATTERN_ERE='(github\.com/heimgewebe/(tools|lenskit)(\.git)?|heimgewebe/(tools|lenskit)([^[:alnum:]_.-]|$)|^[[:space:]]*-[[:space:]]*name:[[:space:]]*(tools|lenskit)[[:space:]]*$|^[[:space:]]*name:[[:space:]]*(tools|lenskit)[[:space:]]*$|ALLOWED_TARGET_REPOS:.*(^|[^[:alnum:]_])(tools|lenskit)([^[:alnum:]_]|$))'
if has_rg; then
  set +e
  rg -n \
    --glob '!reports/sync-logs/**' \
    --glob '!docs/archive/**' \
    --glob '!tools/**' \
    --glob '!scripts/tools/**' \
    --glob '!tests/**' \
    --glob '!scripts/fleet/check_docs_drift.sh' \
    "$LEGACY_PATTERN_RG" .
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    echo "❌ Found stale active repo identity. Use 'repoground' instead."
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
      --exclude-dir='sync-logs' \
      --exclude-dir='archive' \
      --exclude-dir='tools' \
      --exclude-dir='tests' \
      --exclude='check_docs_drift.sh' \
      -e "$LEGACY_PATTERN_ERE" \
      . \
      2>&1
  )
  rc=$?
  set -e

  if [ "$rc" -eq 0 ]; then
    echo "$GREP_OUT"
    echo "❌ Found stale active repo identity. Use 'repoground' instead."
    exit 1
  elif [ "$rc" -eq 1 ]; then
    :
  else
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
