#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure for koalaman/shellcheck
#
# Wenn shellcheck nicht lokal in tools/bin liegt oder falsche Version hat,
# wird die Version aus toolchain.versions.yml geholt und installiert.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
TOOL_NAME="shellcheck"
TOOL_LOCAL="${BIN_DIR}/${TOOL_NAME}"
TOOLCHAIN_KEY="shellcheck"

log() { printf '%s\n' "$*" >&2; }
die() {
  log "ERR: $*"
  exit 1
}

ensure_dir() { mkdir -p -- "${BIN_DIR}"; }
have_cmd() { command -v "$1" > /dev/null 2>&1; }

read_pinned_version() {
  if [[ ! -f "${ROOT_DIR}/toolchain.versions.yml" ]]; then
    die "toolchain.versions.yml nicht gefunden: ${ROOT_DIR}/toolchain.versions.yml"
  fi
  local version
  version=$(grep -E "^\s*${TOOLCHAIN_KEY}:" "${ROOT_DIR}/toolchain.versions.yml" |
    sed -E 's/^\s*[^:]+:\s*//; s/#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' |
    tr -d '\n\r')
  if [[ -z "${version}" ]]; then
    die "Konnte gewünschte Version für ${TOOLCHAIN_KEY} nicht ermitteln."
  fi
  printf '%s' "${version}"
}

version_ok() {
  local v_to_check="$1"
  local req_version_raw="$2"
  # output includes "version: 0.9.0"
  # Extract just the version number from output like "version: 0.9.0"
  local v_have_clean="${v_to_check#v}"
  v_have_clean="${v_have_clean#*: }"  # Remove "version: " prefix if present
  local v_want_clean="${req_version_raw#v}"
  
  # Exact match is always ok
  [[ "${v_have_clean}" == "${v_want_clean}" ]] && return 0
  
  # Allow newer versions using semantic versioning comparison
  local have_major have_minor have_patch
  IFS='.' read -r have_major have_minor have_patch <<< "${v_have_clean}"
  local want_major want_minor want_patch
  IFS='.' read -r want_major want_minor want_patch <<< "${v_want_clean}"
  
  # Remove any non-numeric suffixes
  have_major="${have_major%%[^0-9]*}"
  have_minor="${have_minor%%[^0-9]*}"
  have_patch="${have_patch%%[^0-9]*}"
  want_major="${want_major%%[^0-9]*}"
  want_minor="${want_minor%%[^0-9]*}"
  want_patch="${want_patch%%[^0-9]*}"
  
  # Major version must match
  [[ "${have_major}" -ne "${want_major}" ]] && return 1
  
  # If major matches, newer minor/patch is acceptable
  if [[ "${have_minor}" -gt "${want_minor}" ]]; then
    return 0
  elif [[ "${have_minor}" -eq "${want_minor}" ]] && [[ "${have_patch}" -ge "${want_patch}" ]]; then
    return 0
  fi
  
  return 1
}

compute_target() {
  local os arch
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "$os" in
    linux) ;;
    darwin) ;;
    *) die "OS $os not supported" ;;
  esac

  case "$(uname -m)" in
    x86_64) arch="x86_64" ;;
    aarch64 | arm64)
      # ShellCheck provides darwin.aarch64 binaries starting from v0.10.0
      # For v0.9.0 and earlier, use x86_64 which runs via Rosetta 2 on ARM64 Macs
      if [[ "$os" == "darwin" ]]; then
        arch="x86_64"
      else
        arch="aarch64"
      fi
      ;;
    *) die "Arch $(uname -m) not supported" ;;
  esac

  echo "${os}.${arch}"
}

download_tool() {
  local req_version_raw
  req_version_raw="$(read_pinned_version)"

  log "${TOOL_NAME} nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

  local target
  target="$(compute_target)"
  local filename="shellcheck-${req_version_raw}.${target}.tar.xz"
  local url="https://github.com/koalaman/shellcheck/releases/download/${req_version_raw}/${filename}"

  ensure_dir
  local tmp_bin
  tmp_bin="$(mktemp)"
  trap 'rm -f -- "${tmp_bin-}" 2>/dev/null || true' EXIT

  log "Downloading from ${url}"
  if ! curl -fSL --retry 3 --connect-timeout 10 "${url}" -o "${tmp_bin}"; then
    die "Download fehlgeschlagen: ${url}"
  fi

  # Extract (tar.xz)
  # Contains shellcheck-v0.9.0/shellcheck
  tar -xJf "${tmp_bin}" -C "${BIN_DIR}" --strip-components=1 "shellcheck-${req_version_raw}/shellcheck"
  chmod +x "${TOOL_LOCAL}" || true
  log "${TOOL_NAME} erfolgreich installiert."
}

resolved_tool() {
  if [[ -x "${TOOL_LOCAL}" ]]; then
    echo "${TOOL_LOCAL}"
    return 0
  fi
  if have_cmd "${TOOL_NAME}"; then
    command -v "${TOOL_NAME}"
    return 0
  fi
  return 1
}

cmd_ensure() {
  ensure_dir
  local tool_bin
  local v
  local version_is_ok=false
  local req_version_raw
  req_version_raw="$(read_pinned_version)"

  export PATH="${BIN_DIR}:${PATH}"

  if tool_bin="$(resolved_tool)"; then
    if v="$("${tool_bin}" --version 2>&1)"; then
      if version_ok "${v}" "${req_version_raw}"; then
        version_is_ok=true
      else
        log "WARN: Gefundenes ${TOOL_NAME} hat falsche Version (erwartet: ${req_version_raw})"
      fi
    fi
  fi

  if ! $version_is_ok; then
    download_tool
    if ! tool_bin="$(resolved_tool)"; then
      die "${TOOL_NAME} nach Download nicht verfügbar."
    fi
    v="$("${tool_bin}" --version 2>&1)"
    if ! version_ok "${v}" "${req_version_raw}"; then
      die "Installiertes ${TOOL_NAME} hat immer noch falsche Version."
    fi
  fi

  log "OK: ${TOOL_NAME} ${req_version_raw} verfügbar."
}

case "${1:-ensure}" in
  ensure)
    cmd_ensure "$@"
    ;;
  *)
    die "usage: $0 ensure"
    ;;
esac
