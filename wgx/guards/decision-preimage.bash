#!/usr/bin/env bash
set -euo pipefail

# WGX Guard: decision.preimage presence check (soft)
#
# Purpose:
#   Warn if policy.decision JSON objects appear without a preimage reference.
#   This is intentionally a WARNING (exit 0), not a hard failure.
#
# Contract context:
#   policy.decision currently exists; preimage linking is meant to become visible.
#   The enforcement level can be upgraded later (warn -> fail) once producers comply.

warn() {
  # GitHub Actions annotation if available; otherwise plain stderr.
  local msg="$1"
  local file="${2:-}"
  if [[ -n "${GITHUB_ACTIONS:-}" && -n "${file}" ]]; then
    echo "::warning file=${file}::${msg}"
  else
    echo "WARN: ${msg}${file:+ (${file})}" >&2
  fi
}

info() { echo "INFO: $*" >&2; }

if ! command -v jq > /dev/null 2>&1; then
  warn "jq not found; skipping decision-preimage guard (install jq to enable)"
  exit 0
fi

# Determine candidate JSON files.
#
# Strategy:
#   - In CI with a base ref: only inspect changed *.json
#   - Otherwise: inspect repo-local likely places (contracts/examples) and any *.json under repo (bounded)

files=()

if [[ -n "${GITHUB_BASE_REF:-}" ]] && git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  # Best-effort diff against base
  base="origin/${GITHUB_BASE_REF}"
  if git show-ref --verify --quiet "refs/remotes/${base#origin/}"; then
    mapfile -t files < <(git diff --name-only "$base"...HEAD -- '*.json' 2> /dev/null || true)
  else
    # Fallback: try without remote ref presence
    mapfile -t files < <(git diff --name-only -- '*.json' 2> /dev/null || true)
  fi
else
  # Local mode: focus on typical locations first, then bounded scan
  # We use a combined stream and deduplicate to avoid checking the same file twice.
  mapfile -t files < <(
    {
      if [[ -d contracts/examples ]]; then
        find contracts/examples -type f -name '*.json' -print0 2> /dev/null || true
      fi
      find . -type f -name '*.json' -not -path './.git/*' -print0 2> /dev/null | head -z -n 2000 || true
    } | sed -z 's|^\./||' | sort -z -u | tr '\0' '\n'
  )
fi

if [[ ${#files[@]} -eq 0 ]]; then
  info "No JSON files found to inspect; decision-preimage guard: nothing to do."
  exit 0
fi

missing=0
checked=0

for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue

  # Accept either:
  #   - single JSON object
  #   - JSON array of objects
  #   - newline-delimited JSON is out of scope for this guard

  # Fast reject: invalid json => ignore (other validators should catch)
  if ! jq -e '.' "$f" > /dev/null 2>&1; then
    continue
  fi

  # Single object case: kind == "policy.decision"
  if jq -e 'type=="object" and (.kind? // "")=="policy.decision"' "$f" > /dev/null 2>&1; then
    checked=$((checked + 1))
    if ! jq -e '(.preimage_ref? // "") | length > 0' "$f" > /dev/null 2>&1; then
      warn "policy.decision ohne preimage_ref – Entscheidung ohne expliziten Erkenntnis-Vorlauf (warn-only)" "$f"
      missing=$((missing + 1))
    fi
    continue
  fi

  # Array case: scan elements
  if jq -e 'type=="array"' "$f" > /dev/null 2>&1; then
    # Count and warn per file (not per element) to avoid spam
    # Any element with kind==policy.decision missing preimage_ref triggers warning.
    if jq -e '
      any(.[]?; (type=="object" and (.kind? // "")=="policy.decision"))' "$f" > /dev/null 2>&1; then
      checked=$((checked + 1))
      if jq -e '
        any(.[]?;
          (type=="object" and (.kind? // "")=="policy.decision" and ((.preimage_ref? // "") | length == 0))
        )' "$f" > /dev/null 2>&1; then
        warn "policy.decision in Array ohne preimage_ref gefunden – warn-only" "$f"
        missing=$((missing + 1))
      fi
    fi
  fi
done

info "decision-preimage guard: checked=${checked} file(s) containing policy.decision; warnings=${missing}"
exit 0
