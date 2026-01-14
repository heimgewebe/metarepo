#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure für casey/just – robust & sicher.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/just liegt oder im PATH verfügbar ist.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
JUST_LOCAL="${BIN_DIR}/just"

# Source centralized semver and installer libraries
# shellcheck source=../lib/semver.sh
source "${ROOT_DIR}/scripts/lib/semver.sh"
# shellcheck source=../lib/installer.bash
source "${ROOT_DIR}/scripts/lib/installer.bash"

# Override read_pinned_version to use the library but handle JUST_VERSION env var
read_pinned_version() {
  if [[ -n "${JUST_VERSION:-}" ]]; then
    printf '%s' "${JUST_VERSION}"
    return 0
  fi
  local v
  v="$(inst_read_toolchain_version "just" "${ROOT_DIR}/toolchain.versions.yml")"
  if [[ -z "${v}" ]]; then
    inst_die "Konnte gewünschte just-Version aus toolchain.versions.yml nicht ermitteln."
  fi
  printf '%s' "${v}"
}

detect_libc() {
  # Linux: default to gnu (glibc); allow override
  if [ -n "${JUST_LIBC:-}" ]; then
    echo "$JUST_LIBC"
  elif [ "$(inst_detect_os)" = "linux" ]; then
    # just v1.43.0 only has musl builds for linux
    local req_version_raw
    req_version_raw="$(read_pinned_version)"
    if [ "${req_version_raw#v}" = "1.43.0" ]; then
      echo "musl"
      return
    fi
    if [ -e /lib/ld-musl-x86_64.so.1 ] || [ -e /lib/ld-musl-aarch64.so.1 ]; then
      echo "musl"
    else
      echo "gnu"
    fi
  else
    echo "" # darwin doesn’t use gnu/musl tag
  fi
}

compute_target() {
  local os arch libc
  os="$(inst_detect_os)"
  arch="$(inst_detect_arch)"
  libc="$(detect_libc)"
  if [ "$os" = "darwin" ]; then
    echo "${arch}-apple-darwin"
  else
    echo "${arch}-unknown-${os}${libc:+-$libc}"
  fi
}

download_just() {
  local req_version_raw
  req_version_raw="$(read_pinned_version)"
  local ver_numeric="${req_version_raw#v}"

  inst_log "just nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

  local target
  target="$(compute_target)"
  local filename="just-${ver_numeric}-${target}.tar.gz"
  # Just releases use tags without 'v' (e.g. 1.43.0)
  local tag="${req_version_raw#v}"
  local url="https://github.com/casey/just/releases/download/${tag}/${filename}"
  local checksum_base="https://github.com/casey/just/releases/download/${tag}"

  if [ "${DRY_RUN:-}" = "1" ]; then
    echo "${url}"
    return 0
  fi

  inst_ensure_dir "${BIN_DIR}"
  local tmp_bin tmp_checksum
  tmp_bin="$(mktemp)"
  tmp_checksum="$(mktemp)"
  # Safe cleanup
  trap 'rm -f -- "${tmp_bin-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

  if ! inst_download_file "${url}" "${tmp_bin}"; then
    inst_log "Mögliche Ursachen:"
    inst_log "  - Netzwerkproblem oder GitHub API-Limit"
    inst_log "  - Release ${tag} hat kein Asset ${filename}"
    inst_log "  - Überprüfen Sie: https://github.com/casey/just/releases/tag/${tag}"
    inst_die "Download fehlgeschlagen: ${url}"
  fi

  local checksum_candidates=("SHA256SUMS" "checksums.txt" "checksums")
  local checksum_found=false

  for cand in "${checksum_candidates[@]}"; do
    local c_url="${checksum_base}/${cand}"
    if inst_download_file "${c_url}" "${tmp_checksum}" 2> /dev/null; then
      inst_log "Checksummen geladen: ${cand}"
      checksum_found=true
      break
    fi
  done

  if $checksum_found; then
    inst_log "Verifiziere Checksumme..."
    local expected_sum
    # Format: SHA256  filename
    expected_sum=$(grep "${filename}$" "${tmp_checksum}" | awk '{print $1}' || true)

    if [[ -z "${expected_sum}" ]]; then
      inst_log "WARN: Keine Checksumme für ${filename} in Datei gefunden."
    else
      local actual_sum
      actual_sum="$(inst_calculate_sha256 "${tmp_bin}")"

      if [[ -z "${actual_sum}" ]]; then
        inst_log "WARN: No checksum tool available - skipping checksum verification."
      else
        if [[ "${expected_sum}" != "${actual_sum}" ]]; then
          inst_die "Checksum-Fehler! Erwartet: ${expected_sum}, Ist: ${actual_sum}"
        fi
        inst_log "Checksumme OK: ${actual_sum}"
      fi
    fi
  else
    inst_log "WARN: Konnte keine Checksummen-Datei laden. Überspringe Verifikation."
  fi

  tar -xzf "${tmp_bin}" -C "${BIN_DIR}" just
  chmod +x "${JUST_LOCAL}" || true
  inst_log "just erfolgreich nach ${JUST_LOCAL} installiert."
}

resolved_just() {
  if [[ -x "${JUST_LOCAL}" ]]; then
    echo "${JUST_LOCAL}"
    return 0
  fi
  if inst_have_cmd just; then
    command -v just
    return 0
  fi
  return 1
}

cmd_ensure() {
  inst_ensure_dir "${BIN_DIR}"
  local just_bin
  local v
  local version_is_ok=false
  local req_version_raw
  req_version_raw="$(read_pinned_version)"

  # Prioritize local bin
  export PATH="${BIN_DIR}:${PATH}"

  # Agent-Mode: only verify that just is available, do not download
  if [[ "${AGENT_MODE:-}" != "" ]]; then
    inst_log "Agent-Mode: skipping dynamic just installation"
    if just_bin="$(resolved_just)"; then
      if v="$("${just_bin}" --version 2> /dev/null | cut -d' ' -f2)"; then
        if version_ok "${v}" "${req_version_raw}"; then
          inst_log "OK: just ${v} verfügbar (Agent-Mode)."
          return 0
        else
          inst_log "WARN: Gefundenes just hat falsche Version: ${v} (erwartet: ${req_version_raw})"
          inst_die "just version mismatch in Agent-Mode. Expected: ${req_version_raw}, Found: ${v}"
        fi
      fi
    fi
    inst_die "just not available in Agent-Mode. Please pre-install just ${req_version_raw} or vendor it."
  fi

  if just_bin="$(resolved_just)"; then
    if v="$("${just_bin}" --version 2> /dev/null | cut -d' ' -f2)"; then
      if version_ok "${v}" "${req_version_raw}"; then
        version_is_ok=true
      else
        inst_log "WARN: Gefundenes just hat falsche Version: ${v} (erwartet: ${req_version_raw})"
      fi
    fi
  fi

  if ! $version_is_ok; then
    download_just
    if [ "${DRY_RUN:-}" = "1" ]; then
      return 0
    fi
    if ! just_bin="$(resolved_just)"; then
      inst_die "just nach Download nicht verfügbar."
    fi
    # Verify again
    v="$("${just_bin}" --version | cut -d' ' -f2)"
    if ! version_ok "${v}" "${req_version_raw}"; then
      inst_die "Installiertes just hat immer noch falsche Version: ${v}"
    fi
  fi

  # Symlink if needed
  if [[ "${just_bin}" != "${JUST_LOCAL}" && ! -e "${JUST_LOCAL}" ]]; then
    ln -s -- "${just_bin}" "${JUST_LOCAL}" || true
  fi
  inst_log "OK: just ${v} verfügbar."
}

case "${1:-ensure}" in
  ensure)
    cmd_ensure "$@"
    ;;
  *)
    inst_die "usage: $0 ensure"
    ;;
esac
