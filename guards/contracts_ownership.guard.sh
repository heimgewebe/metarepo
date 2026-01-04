#!/usr/bin/env bash
set -euo pipefail

# WGX Guard: Contract Ownership & Integrity
#
# Enforces Single Source of Truth for contracts.
#
# Rules:
# 1. metarepo (identified by fleet/repos.yml):
#    - MUST contain fleet/repos.yml
#    - MAY modify contracts/**
# 2. contracts-mirror:
#    - MAY modify json/**, proto/** (external/derived schemas)
#    - MUST NOT modify contracts/** (internal contracts belong to metarepo)
# 3. All other repos:
#    - MUST NOT modify contracts/**

warn() { echo "WARN: $*" >&2; }
fail() { echo "FAIL: $*" >&2; exit 1; }
info() { echo "INFO: $*" >&2; }

# --- 1. Repo Identification ---

# Allow override for testing
REPO_NAME="${HG_REPO_NAME:-}"

if [[ -z "$REPO_NAME" ]]; then
  # Try to guess from git remote
  if remote_url=$(git remote get-url origin 2>/dev/null); then
    REPO_NAME=$(basename "$remote_url" .git)
  fi
fi

if [[ -z "$REPO_NAME" ]]; then
  # Fallback to directory name
  REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
fi

info "Identified repo as: $REPO_NAME"

# --- 2. Determine Changed Files ---

CHANGED_FILES=()

if [[ -n "${GITHUB_BASE_REF:-}" ]]; then
  # CI Pull Request
  info "Running in CI mode (PR against ${GITHUB_BASE_REF})"
  git fetch origin "${GITHUB_BASE_REF}" --depth=1 >/dev/null 2>&1 || true
  # Use mapfile to safely handle filenames with spaces (though rare in code)
  mapfile -t CHANGED_FILES < <(git diff --name-only "origin/${GITHUB_BASE_REF}"...HEAD 2>/dev/null || true)
else
  # Local usage
  info "Running in Local mode"
  # Staged + Unstaged changes
  mapfile -t CHANGED_FILES < <({ git diff --name-only --cached; git diff --name-only; } | sort -u)
fi

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  info "No changed files detected. Passing."
  exit 0
fi

# --- 3. Apply Rules ---

# Check if we are physically in the metarepo (filesystem check is stronger than name for this invariant)
IS_METAREPO=false
if [[ -f "fleet/repos.yml" ]]; then
  IS_METAREPO=true
fi

# Invariant: If identified as metarepo by name, it MUST have fleet/repos.yml
if [[ "$REPO_NAME" == "metarepo" ]] && [[ "$IS_METAREPO" == "false" ]]; then
  fail "Repo identified as 'metarepo' but 'fleet/repos.yml' is missing! Integrity violation."
fi

CONTRACTS_MODIFIED=false
for f in "${CHANGED_FILES[@]}"; do
  if [[ "$f" == contracts/* ]]; then
    CONTRACTS_MODIFIED=true
    break
  fi
done

if [[ "$IS_METAREPO" == "true" ]]; then
  # METAREPO: Allowed to modify anything.
  info "Repo is metarepo (fleet/repos.yml present). Contracts modification allowed."
  exit 0
elif [[ "$REPO_NAME" == "contracts-mirror" ]]; then
  # CONTRACTS-MIRROR
  if [[ "$CONTRACTS_MODIFIED" == "true" ]]; then
    fail "Contracts Ownership Violation: 'contracts-mirror' must not modify internal 'contracts/**'. It only mirrors external schemas (json/**, proto/**). Please define contracts in metarepo."
  fi
  info "Repo is contracts-mirror. No internal contracts touched. OK."
  exit 0
else
  # ALL OTHER REPOS
  if [[ "$CONTRACTS_MODIFIED" == "true" ]]; then
    warn "This repository should not modify internal contracts."
    fail "Contracts Ownership Violation: Internal contracts ('contracts/**') MUST only be modified in 'metarepo'. Please move schema to metarepo/contracts/ and consume it here."
  fi
  info "Repo is $REPO_NAME (satellite). No internal contracts touched. OK."
  exit 0
fi
