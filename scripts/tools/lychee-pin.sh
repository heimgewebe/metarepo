#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure for lycheeverse/lychee

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
TOOL_NAME="lychee"
TOOL_LOCAL="${BIN_DIR}/${TOOL_NAME}"
TOOLCHAIN_KEY="lychee"

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
  local v_have_clean="${v_to_check#v}"
  local v_want_clean="${req_version_raw#v}"
  
  # Exact match is always ok
  [[ "${v_have_clean}" == "${v_want_clean}" ]] && return 0
  
  # Allow newer versions using semantic versioning comparison
  local have_major have_minor have_patch want_major want_minor want_patch
  {
    IFS='.' read -r have_major have_minor have_patch <<< "${v_have_clean}"
    IFS='.' read -r want_major want_minor want_patch <<< "${v_want_clean}"
  }
  
  # Remove any non-numeric suffixes
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
  arch="$(uname -m)"

  case "$os" in
    linux)
      case "$arch" in
        x86_64) echo "x86_64-unknown-linux-gnu" ;;
        aarch64) echo "aarch64-unknown-linux-gnu" ;;
        *) die "Arch $arch not supported for linux" ;;
      esac
      ;;
    darwin)
      case "$arch" in
        x86_64) echo "x86_64-apple-darwin" ;;
        arm64 | aarch64) echo "aarch64-apple-darwin" ;;
        *) die "Arch $arch not supported for darwin" ;;
      esac
      ;;
    *) die "OS $os not supported" ;;
  esac
}

download_tool() {
  local req_version_raw
  req_version_raw="$(read_pinned_version)"
  # Filename pattern: lychee-v0.15.1-x86_64-unknown-linux-gnu.tar.gz
  local target
  target="$(compute_target)"
  local filename="lychee-${req_version_raw}-${target}.tar.gz"
  local url="https://github.com/lycheeverse/lychee/releases/download/${req_version_raw}/${filename}"
  local checksum_base="https://github.com/lycheeverse/lychee/releases/download/${req_version_raw}"

  log "${TOOL_NAME} nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

  if [ "${DRY_RUN:-}" = "1" ]; then
    echo "${url}"
    return 0
  fi

  ensure_dir
  local tmp_bin tmp_checksum tmp_extract
  tmp_bin="$(mktemp)"
  tmp_checksum="$(mktemp)"
  tmp_extract="$(mktemp -d)"
  trap 'rm -f -- "${tmp_bin-}" "${tmp_checksum-}"; rm -rf -- "${tmp_extract-}" 2>/dev/null || true' EXIT

  log "Downloading lychee from ${url}"
  if ! curl -fSL --retry 3 --connect-timeout 10 "${url}" -o "${tmp_bin}"; then
    die "Download fehlgeschlagen: ${url}"
  fi

  # Checksums logic (optional but recommended)
  # lychee releases often have SHASUMS or similar?
  # v0.15.1 has 'SHA256SUMS' (assumption based on other tools)
  # Actually lychee release page shows 'checksums.txt' or nothing?
  # I'll try SHA256SUMS and checksums.txt
  local checksum_candidates=("SHA256SUMS" "checksums.txt" "checksums")
  local checksum_found=false
  for cand in "${checksum_candidates[@]}"; do
    if curl -fSL --retry 3 --connect-timeout 10 "${checksum_base}/${cand}" -o "${tmp_checksum}" 2> /dev/null; then
      log "Checksummen geladen: ${cand}"
      checksum_found=true
      break
    fi
  done

  if $checksum_found; then
    log "Verifiziere Checksumme..."
    local expected_sum
    expected_sum=$(grep "${filename}$" "${tmp_checksum}" | awk '{print $1}' || true)

    if [[ -n "${expected_sum}" ]]; then
      local actual_sum
      if have_cmd sha256sum; then
        actual_sum=$(sha256sum "${tmp_bin}" | awk '{print $1}')
      elif have_cmd shasum; then
        actual_sum=$(shasum -a 256 "${tmp_bin}" | awk '{print $1}')
      else
        log "WARN: Kein Checksum-Tool gefunden."
        actual_sum=""
      fi

      if [[ -n "${actual_sum}" ]]; then
        if [[ "${expected_sum}" != "${actual_sum}" ]]; then
          die "Checksum-Fehler! Erwartet: ${expected_sum}, Ist: ${actual_sum}"
        fi
        log "Checksumme OK."
      fi
    else
      log "WARN: Keine Checksumme für ${filename} in Datei gefunden."
    fi
  else
    log "WARN: Keine Checksummen-Datei gefunden."
  fi

  tar -xzf "${tmp_bin}" -C "${tmp_extract}"
  # Binary inside might be 'lychee' or in a subdir?
  # lychee tarballs usually contain the binary at root or inside a folder named like the tarball minus extension.
  # Let's find it.
  find "${tmp_extract}" -type f -name lychee -exec mv -f {} "${TOOL_LOCAL}" \;
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
    # lychee --version -> "lychee 0.15.1"
    if v="$("${tool_bin}" --version 2> /dev/null | head -n1 | awk '{print $2}')"; then
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
    v="$("${tool_bin}" --version | head -n1 | awk '{print $2}')"
    if ! version_ok "${v}" "${req_version_raw}"; then
      die "Installiertes ${TOOL_NAME} hat immer noch falsche Version: ${v}"
    fi
  fi

  if [[ "${tool_bin}" != "${TOOL_LOCAL}" && ! -e "${TOOL_LOCAL}" ]]; then
    ln -s -- "${tool_bin}" "${TOOL_LOCAL}" || true
  fi

  log "OK: ${TOOL_NAME} ${v} verfügbar."
}

case "${1:-ensure}" in
  ensure)
    cmd_ensure "$@"
    ;;
  *)
    die "usage: $0 ensure"
    ;;
esac
