#!/usr/bin/env bash
# Shared semantic versioning utilities for tool pin scripts
# Usage: source scripts/lib/semver.sh

# semver_compare: Compare two versions with semantic versioning rules
# Args:
#   $1: version_have (e.g., "4.50.1" or "v4.50.1")
#   $2: version_want (e.g., "v4.49.2")
#   $3: strict mode (optional, default: 0)
#       0 = allow newer compatible versions (default)
#       1 = require exact match (strict pin)
# Returns:
#   0 if version_have is acceptable
#   1 if version_have is not acceptable
#
# SemVer Rules:
#   - Exact match always passes
#   - For major version 0.x: minor must match exactly, patch can be >=
#   - For major version >= 1: major must match, minor/patch can be newer
#   - Strict mode: only exact match passes
semver_compare() {
  local v_have="$1"
  local v_want="$2"
  local strict="${3:-0}"
  
  # Clean version strings (remove quotes and 'v' prefix)
  local v_want_clean
  v_want_clean="$(echo "${v_want}" | tr -d "'\"v")"
  local v_have_clean
  v_have_clean="$(echo "${v_have}" | tr -d "v")"
  
  # Exact match is always ok
  [[ "${v_have_clean}" == "${v_want_clean}" ]] && return 0
  
  # In strict mode, only exact match is acceptable
  [[ "${strict}" == "1" ]] && return 1
  
  # Split versions into major.minor.patch
  # Use brace grouping to isolate IFS modification
  local have_major have_minor have_patch want_major want_minor want_patch
  {
    IFS='.' read -r have_major have_minor have_patch <<< "${v_have_clean}"
    IFS='.' read -r want_major want_minor want_patch <<< "${v_want_clean}"
  }
  
  # Remove any non-numeric suffixes (e.g., "1.2.3-beta" -> "1.2.3")
  have_major="${have_major%%[^0-9]*}"
  have_minor="${have_minor%%[^0-9]*}"
  have_patch="${have_patch%%[^0-9]*}"
  want_major="${want_major%%[^0-9]*}"
  want_minor="${want_minor%%[^0-9]*}"
  want_patch="${want_patch%%[^0-9]*}"
  
  # Default to 0 if empty
  have_major="${have_major:-0}"
  have_minor="${have_minor:-0}"
  have_patch="${have_patch:-0}"
  want_major="${want_major:-0}"
  want_minor="${want_minor:-0}"
  want_patch="${want_patch:-0}"
  
  # Major version must match
  [[ "${have_major}" -ne "${want_major}" ]] && return 1
  
  # Special handling for 0.x versions (unstable API per SemVer spec)
  # In 0.x, minor version changes can be breaking, so require exact minor match
  if [[ "${want_major}" -eq 0 ]]; then
    # For 0.0.x: everything can be breaking, require exact match
    if [[ "${want_minor}" -eq 0 ]]; then
      if [[ "${have_minor}" -eq "${want_minor}" ]] && [[ "${have_patch}" -eq "${want_patch}" ]]; then
        return 0
      fi
      return 1
    fi
    # For 0.x (x > 0): minor must match exactly, only patch can be >=
    if [[ "${have_minor}" -eq "${want_minor}" ]] && [[ "${have_patch}" -ge "${want_patch}" ]]; then
      return 0
    fi
    return 1
  fi
  
  # For major >= 1: newer minor/patch is acceptable
  if [[ "${have_minor}" -gt "${want_minor}" ]]; then
    return 0
  elif [[ "${have_minor}" -eq "${want_minor}" ]] && [[ "${have_patch}" -ge "${want_patch}" ]]; then
    return 0
  fi
  
  # Have version is older than want
  return 1
}

# version_ok: Wrapper for backward compatibility
# Checks if version is acceptable, with optional strict mode via environment
version_ok() {
  local v_have="$1"
  local v_want="$2"
  local strict="${STRICT_VERSION_PIN:-0}"
  semver_compare "${v_have}" "${v_want}" "${strict}"
}
