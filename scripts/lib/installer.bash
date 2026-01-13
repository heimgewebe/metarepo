#!/usr/bin/env bash
# Shared installer utilities for tool pinning scripts.
# Contains: logging, standardized OS/Arch detection, robust checksum calculation, and version parsing.

log() { printf '%s\n' "$*" >&2; }
die() {
  log "ERR: $*"
  exit 1
}

ensure_dir() {
  if [[ -z "${1:-}" ]]; then
    die "ensure_dir: missing argument"
  fi
  mkdir -p -- "$1"
}

have_cmd() { command -v "$1" > /dev/null 2>&1; }

require_cmd() {
  local cmd="$1"
  local hint="${2:-}"
  if ! have_cmd "${cmd}"; then
    if [[ -n "${hint}" ]]; then
      die "Benötigtes Kommando '${cmd}' fehlt. ${hint}"
    else
      die "Benötigtes Kommando '${cmd}' fehlt."
    fi
  fi
}

# detect_os_normalized: returns 'linux' or 'darwin'
detect_os_normalized() {
  local os
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "${os}" in
    linux|darwin) echo "${os}" ;;
    *) die "Unsupported OS: ${os}" ;;
  esac
}

# detect_arch_normalized: returns 'x86_64' or 'aarch64'
detect_arch_normalized() {
  local arch
  arch="$(uname -m)"
  case "${arch}" in
    x86_64|amd64) echo "x86_64" ;;
    arm64|aarch64) echo "aarch64" ;;
    *) echo "${arch}" ;; # Fallback for others
  esac
}

# read_toolchain_version:
# usage: read_toolchain_version <tool_name> <toolchain_file>
read_toolchain_version() {
  local tool_name="$1"
  local toolchain_file="$2"

  if [[ ! -f "${toolchain_file}" ]]; then
    die "toolchain file not found: ${toolchain_file}"
  fi

  local version
  # Robust parsing logic (from just-pin.sh/yq-pin.sh)
  version=$(grep -E "^[[:space:]]*${tool_name}[[:space:]]*:" "${toolchain_file}" | head -n1 |
    sed -E 's/^[[:space:]]*[^:]+:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' |
    tr -d '\n\r')

  if [[ -z "${version}" ]]; then
    # Do not die here, let the caller handle empty version (e.g. try env var first)
    # But usually this is called when we expect it.
    # For now, return empty string.
    echo ""
  else
    printf '%s' "${version}"
  fi
}

# calculate_sha256:
# usage: calculate_sha256 <filepath>
# Returns only the hex hash to stdout.
calculate_sha256() {
  local file="$1"
  if [[ ! -f "${file}" ]]; then
    die "calculate_sha256: file not found: ${file}"
  fi

  if have_cmd sha256sum; then
    sha256sum "${file}" | awk '{print $1}'
  elif have_cmd shasum; then
    shasum -a 256 "${file}" | awk '{print $1}'
  elif have_cmd python3; then
    python3 -c "import hashlib; print(hashlib.sha256(open('${file}', 'rb').read()).hexdigest())"
  elif have_cmd python; then
    python -c "import hashlib; print(hashlib.sha256(open('${file}', 'rb').read()).hexdigest())"
  else
    # Return empty string to indicate failure to calculate
    echo ""
  fi
}

# download_file:
# usage: download_file <url> <dest>
download_file() {
  local url="$1"
  local dest="$2"

  log "Downloading ${url} -> ${dest}"
  if ! curl --fail --location --retry 3 --connect-timeout 10 -o "${dest}" "${url}"; then
    log "Download failed: ${url}"
    return 1
  fi
  return 0
}
