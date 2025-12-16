#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure for mvdan/sh (shfmt)
#
# Wenn shfmt nicht lokal in tools/bin liegt oder falsche Version hat,
# wird die Version aus toolchain.versions.yml geholt und installiert.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
TOOL_NAME="shfmt"
TOOL_LOCAL="${BIN_DIR}/${TOOL_NAME}"
TOOLCHAIN_KEY="shfmt"

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
  # shfmt --version output: "v3.8.0"
  local v_expect="${req_version_raw}"
  if [[ "${v_expect}" != v* ]]; then
    v_expect="v${v_expect}"
  fi
  [[ "${v_to_check}" == "${v_expect}" ]]
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
    x86_64) arch="amd64" ;;
    aarch64 | arm64) arch="arm64" ;;
    *) die "Arch $(uname -m) not supported" ;;
  esac

  echo "${os}_${arch}"
}

download_tool() {
  local req_version_raw
  req_version_raw="$(read_pinned_version)"

  log "${TOOL_NAME} nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

  local target
  target="$(compute_target)"
  # mvdan/sh releases require 'v' prefix in both tag and filename
  local version_tag="${req_version_raw}"
  if [[ "${version_tag}" != v* ]]; then
    version_tag="v${version_tag}"
  fi
  local filename="shfmt_${version_tag}_${target}"
  local url="https://github.com/mvdan/sh/releases/download/${version_tag}/${filename}"

  ensure_dir
  local tmp_bin
  tmp_bin="$(mktemp)"
  trap 'rm -f -- "${tmp_bin-}" 2>/dev/null || true' EXIT

  log "Downloading from ${url}"
  if ! curl -fSL --retry 3 --connect-timeout 10 "${url}" -o "${tmp_bin}"; then
    die "Download fehlgeschlagen: ${url}"
  fi

  mv "${tmp_bin}" "${TOOL_LOCAL}"
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
        log "WARN: Gefundenes ${TOOL_NAME} hat falsche Version: ${v} (erwartet: ${req_version_raw})"
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
      die "Installiertes ${TOOL_NAME} hat immer noch falsche Version: ${v}"
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
