#!/usr/bin/env bash
set -euo pipefail

#
# Heimgewebe Agent-Mode Check
#
# Ziel: einfache statische Prüfung, ob dieses Repo offensichtliche
# agent-inkompatible Muster enthält (Netzwerkaufrufe, dynamische
# Installationen) in Workflows und Scripts.
#
# Note: This is an advisory tool. Patterns that are properly guarded by
# AGENT_MODE conditionals are acceptable but may still be flagged.
#

ROOT_DIR="${1:-.}"

# Configurable threshold for maximum warnings before failing
MAX_WARNINGS="${MAX_AGENT_MODE_WARNINGS:-50}"

echo "Agent-Mode: scanning repository at: ${ROOT_DIR}"

warnings=0

check_pattern() {
  local pattern="$1"
  local context="$2"

  # Build exclude arguments
  local exclude_args=(
    --exclude-dir='.git'
    --exclude-dir='man'
    --exclude='*.md'
    --exclude='agent-mode-check.sh'
    --exclude='agent-mode.md'
    --exclude='*.1'    # man pages
    --exclude='*.json' # JSON schema files
    --exclude='*.toml' # Config files like .lychee.toml
  )

  # Use unique temporary file to avoid race conditions
  local tmpfile
  tmpfile="$(mktemp)"
  trap 'rm -f "${tmpfile}"' RETURN

  if grep -RIn "${exclude_args[@]}" "${pattern}" "${ROOT_DIR}" > "${tmpfile}" 2> /dev/null; then
    echo "::warning::Agent-Mode: found pattern '${pattern}' in ${context}"
    head -10 "${tmpfile}"
    warnings=$((warnings + 1))
  fi
}

echo "Agent-Mode: checking for outbound network usage in workflows and scripts…"

# Note: Some of these may be acceptable if guarded by AGENT_MODE checks
check_pattern 'curl http' ".github/workflows, scripts"
check_pattern 'curl https' ".github/workflows, scripts"

echo "Agent-Mode: checking for dynamic installs (npm/pip/go/cargo)…"

# Use extended regex with -E for better pattern matching
check_pattern 'pip install' "Python/pip installs"
check_pattern 'npm install' "Node/npm installs"
check_pattern 'npm i -g' "Node/npm global installs"
check_pattern 'cargo install' "Rust/cargo installs"

if [[ "${AGENT_MODE:-}" != "" ]]; then
  echo "Agent-Mode: AGENT_MODE is set (${AGENT_MODE})."
  echo "Agent-Mode: Found ${warnings} pattern(s) that may need review."
  echo ""
  echo "Note: Many of these patterns may be acceptable if they are:"
  echo "  - Guarded by 'if: \${{ env.AGENT_MODE == \"\" }}' conditionals"
  echo "  - In error messages or documentation"
  echo "  - In scripts that check AGENT_MODE before executing"
  echo ""

  # Threshold of 50 chosen as reasonable balance: allows some advisory warnings
  # while catching repos with many unguarded violations.
  # Can be overridden via MAX_AGENT_MODE_WARNINGS env var.
  if [[ "${warnings}" -gt "${MAX_WARNINGS}" ]]; then
    echo "::error::Too many potential Agent-Mode violations (${warnings} > ${MAX_WARNINGS}). Please review and guard with AGENT_MODE checks."
    exit 1
  else
    echo "::notice::Agent-Mode check complete. Review warnings above to ensure patterns are properly guarded."
  fi
else
  echo "::notice::Agent-Mode: check completed in advisory mode (AGENT_MODE not set)."
  echo "          Found ${warnings} pattern(s). These should be reviewed and guarded when AGENT_MODE=1."
fi
