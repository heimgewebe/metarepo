#!/usr/bin/env bash
# Shared installer utilities for tool pinning scripts.
# Contains: logging, standardized OS/Arch detection, robust checksum calculation, and version parsing.

# Namespace: inst_ (installer)

inst_log() {
  if [[ "${INSTALLER_QUIET:-}" != "1" ]]; then
    printf '%s\n' "$*" >&2
  fi
}

inst_die() {
  # Errors always print (even if INSTALLER_QUIET=1)
  printf 'ERR: %s\n' "$*" >&2
  exit 1
}

inst_ensure_dir() {
  if [[ -z "${1:-}" ]]; then
    inst_die "inst_ensure_dir: missing argument"
  fi
  mkdir -p -- "$1"
}

inst_have_cmd() { command -v "$1" > /dev/null 2>&1; }

inst_require_cmd() {
  local cmd="$1"
  local hint="${2:-}"
  if ! inst_have_cmd "${cmd}"; then
    if [[ -n "${hint}" ]]; then
      inst_die "Benötigtes Kommando '${cmd}' fehlt. ${hint}"
    else
      inst_die "Benötigtes Kommando '${cmd}' fehlt."
    fi
  fi
}

# inst_detect_os: returns 'linux' or 'darwin'
inst_detect_os() {
  local os
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "${os}" in
    linux|darwin) echo "${os}" ;;
    *) inst_die "Unsupported OS: ${os}" ;;
  esac
}

# inst_detect_arch: returns 'x86_64' or 'aarch64'
inst_detect_arch() {
  local arch
  arch="$(uname -m)"
  case "${arch}" in
    x86_64|amd64) echo "x86_64" ;;
    arm64|aarch64) echo "aarch64" ;;
    *) echo "${arch}" ;; # Fallback for others
  esac
}

# inst_read_toolchain_version:
# usage: inst_read_toolchain_version <tool_name> <toolchain_file>
inst_read_toolchain_version() {
  local tool_name="$1"
  local toolchain_file="$2"

  if [[ ! -f "${toolchain_file}" ]]; then
    inst_die "toolchain file not found: ${toolchain_file}"
  fi

  local version
  # Robust parsing logic (from just-pin.sh/yq-pin.sh)
  version=$(grep -E "^[[:space:]]*${tool_name}[[:space:]]*:" "${toolchain_file}" | head -n1 |
    sed -E 's/^[[:space:]]*[^:]+:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' |
    tr -d '\n\r')

  if [[ -z "${version}" ]]; then
    # Return empty string
    echo ""
  else
    printf '%s' "${version}"
  fi
}

# inst_calculate_sha256:
# usage: inst_calculate_sha256 <filepath>
# Returns only the hex hash to stdout.
inst_calculate_sha256() {
  local file="$1"
  if [[ ! -f "${file}" ]]; then
    inst_die "inst_calculate_sha256: file not found: ${file}"
  fi

  if inst_have_cmd sha256sum; then
    sha256sum "${file}" | awk '{print $1}'
  elif inst_have_cmd shasum; then
    shasum -a 256 "${file}" | awk '{print $1}'
  elif inst_have_cmd python3; then
    python3 -c "import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())" "$file"
  elif inst_have_cmd python; then
    python -c "import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())" "$file"
  else
    # Return empty string to indicate failure to calculate
    echo ""
  fi
}

# inst_download_file:
# usage: inst_download_file <url> <dest>
inst_download_file() {
  local url="$1"
  local dest="$2"
  local max_time="${CURL_MAX_TIME:-60}"

  inst_log "Downloading ${url} -> ${dest}"

  # -f: fail on server errors (404, 500) without outputting the response body
  # -s: silent mode (no progress bar)
  # -S: show error message if it fails (when used with -s)
  # -L: follow redirects
  if ! curl -fsSL --retry 3 --connect-timeout 10 --max-time "${max_time}" -o "${dest}" "${url}"; then
    inst_log "Download failed: ${url}"
    return 1
  fi
  return 0
}
