#!/usr/bin/env bash
set -euo pipefail

#
# Heimgewebe Agent-Mode Check
#
# Ziel: einfache statische Prüfung, ob dieses Repo offensichtliche
# agent-inkompatible Muster enthält (Netzwerkaufrufe, dynamische
# Installationen) in Workflows und Scripts.
#

ROOT_DIR="${1:-.}"

echo "Agent-Mode: scanning repository at: ${ROOT_DIR}"

fail=0

check_pattern() {
  local pattern="$1"
  local context="$2"

  if grep -RIn --exclude-dir='.git' --exclude='*.md' --exclude='agent-mode-check.sh' "${pattern}" "${ROOT_DIR}" >/tmp/agent-mode-hit.txt 2>/dev/null; then
    echo "::warning::Agent-Mode: found disallowed pattern '${pattern}' in ${context}"
    cat /tmp/agent-mode-hit.txt
    rm -f /tmp/agent-mode-hit.txt
    fail=1
  fi
}

echo "Agent-Mode: checking for outbound network usage in workflows and scripts…"

# Offensichtliche Netzwerkzugriffe
check_pattern 'api.github.com' ".github/workflows, scripts"
check_pattern 'raw.githubusercontent.com' ".github/workflows, scripts"
check_pattern 'curl http' ".github/workflows, scripts"
check_pattern 'curl https' ".github/workflows, scripts"
check_pattern 'wget http' ".github/workflows, scripts"
check_pattern 'wget https' ".github/workflows, scripts"

echo "Agent-Mode: checking for dynamic installs (npm/pip/go/cargo)…"

check_pattern 'npm install' "Node/npm installs"
check_pattern 'pip install' "Python/pip installs"
check_pattern 'go install' "Go installs"
check_pattern 'cargo install' "Rust/cargo installs"

echo "Agent-Mode: checking for curl | bash patterns…"
check_pattern 'curl .*bash' "curl | bash"
check_pattern 'curl .*sh' "curl | sh"

if [[ "${AGENT_MODE:-}" != "" ]]; then
  echo "Agent-Mode: AGENT_MODE is set (${AGENT_MODE}), enforcing strict failure on hits."
fi

if [[ "${fail}" -ne 0 ]]; then
  if [[ "${AGENT_MODE:-}" != "" ]]; then
    echo "::error::Agent-Mode violations detected. See warnings above."
    exit 1
  else
    echo "::warning::Agent-Mode violations detected (but AGENT_MODE is not set)."
    echo "          Treat this as advisory in normal CI, strict in Agent-Mode."
  fi
else
  echo "Agent-Mode: no obvious violations found."
fi
