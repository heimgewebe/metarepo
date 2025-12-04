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
  [[ "${v_to_check}" == *"${req_version_raw#v}"* ]]
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
      # ShellCheck doesn't provide darwin.aarch64 binaries for some versions
      # Use x86_64 version which runs via Rosetta 2 on ARM64 Macs
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
