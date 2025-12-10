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

echo "Agent-Mode: scanning repository at: ${ROOT_DIR}"

fail=0
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
    --exclude='*.1'  # man pages
    --exclude='*.json' # JSON schema files
    --exclude='*.toml' # Config files like .lychee.toml
  )

  if grep -RIn "${exclude_args[@]}" "${pattern}" "${ROOT_DIR}" >/tmp/agent-mode-hit.txt 2>/dev/null; then
    echo "::warning::Agent-Mode: found pattern '${pattern}' in ${context}"
    cat /tmp/agent-mode-hit.txt | head -10
    rm -f /tmp/agent-mode-hit.txt
    warnings=$((warnings + 1))
  fi
}

echo "Agent-Mode: checking for outbound network usage in workflows and scripts…"

# Note: Some of these may be acceptable if guarded by AGENT_MODE checks
check_pattern 'curl http' ".github/workflows, scripts"
check_pattern 'curl https' ".github/workflows, scripts"

echo "Agent-Mode: checking for dynamic installs (npm/pip/go/cargo)…"

check_pattern '\bpip install' "Python/pip installs"
check_pattern '\bnpm install' "Node/npm installs"
check_pattern '\bnpm i -g' "Node/npm global installs"
check_pattern '\bcargo install' "Rust/cargo installs"

if [[ "${AGENT_MODE:-}" != "" ]]; then
  echo "Agent-Mode: AGENT_MODE is set (${AGENT_MODE})."
  echo "Agent-Mode: Found ${warnings} pattern(s) that may need review."
  echo ""
  echo "Note: Many of these patterns may be acceptable if they are:"
  echo "  - Guarded by 'if: \${{ env.AGENT_MODE == \"\" }}' conditionals"
  echo "  - In error messages or documentation"
  echo "  - In scripts that check AGENT_MODE before executing"
  echo ""
  
  if [[ "${warnings}" -gt 50 ]]; then
    echo "::error::Too many potential Agent-Mode violations (${warnings}). Please review and guard with AGENT_MODE checks."
    exit 1
  else
    echo "::notice::Agent-Mode check complete. Review warnings above to ensure patterns are properly guarded."
  fi
else
  echo "::notice::Agent-Mode: check completed in advisory mode (AGENT_MODE not set)."
  echo "          Found ${warnings} pattern(s). These should be reviewed and guarded when AGENT_MODE=1."
fi
