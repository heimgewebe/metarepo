#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure for rhysd/actionlint

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
TOOL_NAME="actionlint"
TOOL_LOCAL="${BIN_DIR}/${TOOL_NAME}"
TOOLCHAIN_KEY="actionlint"

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
  # Parse version from toolchain.versions.yml robustly:
  # 1. Remove key prefix (up to and including ':')
  # 2. Strip comments (everything after '#')
  # 3. Trim leading and trailing whitespace
  # 4. Remove surrounding quotes (double or single)
  # 5. Remove line breaks
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
    x86_64) arch="amd64" ;;
    aarch64 | arm64) arch="arm64" ;;
    *) die "Arch $(uname -m) not supported" ;;
  esac

  echo "${os}_${arch}"
}

download_tool() {
  local req_version_raw
  req_version_raw="$(read_pinned_version)"
  local ver_numeric="${req_version_raw#v}"

  log "${TOOL_NAME} nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

  local target
  target="$(compute_target)"
  local filename="${TOOL_NAME}_${ver_numeric}_${target}.tar.gz"
  local url="https://github.com/rhysd/actionlint/releases/download/${req_version_raw}/${filename}"
  local checksum_base="https://github.com/rhysd/actionlint/releases/download/${req_version_raw}"

  ensure_dir
  local tmp_bin tmp_checksum
  tmp_bin="$(mktemp)"
  tmp_checksum="$(mktemp)"
  trap 'rm -f -- "${tmp_bin-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

  log "Downloading actionlint from ${url}"
  log "Version: ${req_version_raw}, Target: ${target}, Filename: ${filename}"
  if ! curl -fSL --retry 3 --connect-timeout 10 "${url}" -o "${tmp_bin}"; then
    log "FEHLER: Download von actionlint fehlgeschlagen"
    log "URL: ${url}"
    log "Mögliche Ursachen:"
    log "  - Netzwerkproblem oder GitHub API-Limit"
    log "  - Release ${req_version_raw} hat kein Asset ${filename}"
    log "  - Überprüfen Sie: https://github.com/rhysd/actionlint/releases/tag/${req_version_raw}"
    die "Download fehlgeschlagen: ${url}"
  fi

  local checksum_candidates=("checksums.txt" "checksums" "SHA256SUMS")
  local checksum_found=false

  for cand in "${checksum_candidates[@]}"; do
    local c_url="${checksum_base}/${cand}"
    log "Versuche Checksummen von ${c_url}..."
    if curl -fSL --retry 3 --connect-timeout 10 "${c_url}" -o "${tmp_checksum}"; then
      log "Checksummen geladen: ${cand}"
      checksum_found=true
      break
    fi
  done

  if $checksum_found; then
    log "Verifiziere Checksumme..."
    local expected_sum
    expected_sum=$(grep "${filename}$" "${tmp_checksum}" | awk '{print $1}' || true)

    if [[ -z "${expected_sum}" ]]; then
      log "WARN: Keine Checksumme für ${filename} gefunden."
    else
      local actual_sum
      if have_cmd sha256sum; then
        actual_sum=$(sha256sum "${tmp_bin}" | awk '{print $1}')
      elif have_cmd shasum; then
        actual_sum=$(shasum -a 256 "${tmp_bin}" | awk '{print $1}')
      elif have_cmd python3; then
        log "Using Python3 fallback for SHA256 checksum..."
        actual_sum=$(python3 -c "import hashlib; print(hashlib.sha256(open('${tmp_bin}', 'rb').read()).hexdigest())")
      elif have_cmd python; then
        log "Using Python fallback for SHA256 checksum..."
        actual_sum=$(python -c "import hashlib; print(hashlib.sha256(open('${tmp_bin}', 'rb').read()).hexdigest())")
      else
        log "WARN: No checksum tool (sha256sum, shasum, python) available - skipping checksum verification."
        actual_sum=""
      fi

      if [[ -n "${actual_sum}" ]]; then
        if [[ "${expected_sum}" != "${actual_sum}" ]]; then
          die "Checksum-Fehler! Erwartet: ${expected_sum}, Ist: ${actual_sum}"
        fi
        log "Checksumme OK: ${actual_sum}"
      fi
    fi
  else
    log "WARN: Konnte keine Checksummen-Datei laden. Überspringe Verifikation."
  fi

  tar -xzf "${tmp_bin}" -C "${BIN_DIR}" actionlint
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
    # actionlint -version output: "1.7.9" (no v, sometimes)
    if v="$("${tool_bin}" -version 2> /dev/null | head -n1 | awk '{print $1}' | tr -d 'v')"; then
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
    v="$("${tool_bin}" -version | head -n1 | awk '{print $1}' | tr -d 'v')"
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
