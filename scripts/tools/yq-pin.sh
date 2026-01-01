#!/usr/bin/env bash
set -euxo pipefail
# Pin & Ensure für mikefarah/yq v4.x – standardmäßig offline zur Laufzeit.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/yq liegt oder im PATH verfügbar ist.
# Optionaler Download ist NUR erlaubt, wenn ALLOW_NET=1 gesetzt ist.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
YQ_LOCAL="${BIN_DIR}/yq"

log() { printf '%s\n' "$*" >&2; }
die() {
  log "ERR: $*"
  exit 1
}

ensure_dir() { mkdir -p -- "${BIN_DIR}"; }
have_cmd() { command -v "$1" > /dev/null 2>&1; }

version_ok() {
  local v_have="$1"
  local v_want="$2"
  local v_want_clean
  v_want_clean="$(echo "${v_want}" | tr -d "'\"v")"
  local v_have_clean
  v_have_clean="$(echo "${v_have}" | tr -d "v")"
  
  # Exact match is always ok
  [[ "${v_have_clean}" == "${v_want_clean}" ]] && return 0
  
  # Allow newer versions using semantic versioning comparison
  # Split versions into major.minor.patch
  local have_major have_minor have_patch
  IFS='.' read -r have_major have_minor have_patch <<< "${v_have_clean}"
  local want_major want_minor want_patch
  IFS='.' read -r want_major want_minor want_patch <<< "${v_want_clean}"
  
  # Remove any non-numeric suffixes (e.g., "1.2.3-beta" -> "1.2.3")
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
  
  # Have version is older than want
  return 1
}

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

read_pinned_version() {
  if [[ ! -f "${ROOT_DIR}/toolchain.versions.yml" ]]; then
    die "toolchain.versions.yml nicht gefunden: ${ROOT_DIR}/toolchain.versions.yml"
  fi

  # Parse version from toolchain.versions.yml robustly using grep/sed.
  # Do NOT rely on `yq` here to avoid bootstrap paradox (wrong yq in PATH).
  local version
  version="$(
    grep -E '^[[:space:]]*yq[[:space:]]*:' "${ROOT_DIR}/toolchain.versions.yml" | head -n1 |
      sed -E 's/^[[:space:]]*[^:]+:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' |
      tr -d '\n\r'
  )"

  if [[ -z "${version}" ]]; then
    die "Konnte gewünschte yq-Version aus toolchain.versions.yml nicht ermitteln."
  fi
  printf '%s' "${version}"
}

download_yq() {
  # Default: OFFLINE. Download only when explicitly allowed.
  if [[ "${ALLOW_NET:-}" != "1" ]]; then
    die "yq fehlt/inkompatibel und Download ist deaktiviert. Setze ALLOW_NET=1, oder lege ein gepinntes Binary nach ${YQ_LOCAL}."
  fi

  ensure_dir
  log "yq nicht gefunden/inkompatibel. Download ist erlaubt (ALLOW_NET=1)."

  require_cmd curl "Bitte curl installieren oder in PATH bereitstellen."

  local os
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "${os}" in
    linux | darwin) ;;
    *) die "Nicht unterstütztes Betriebssystem für automatischen yq-Download: ${os}" ;;
  esac

  local arch
  arch="$(uname -m)"
  case "${arch}" in
    x86_64) arch="amd64" ;;
    aarch64 | arm64) arch="arm64" ;;
    *) die "Nicht unterstützte Architektur für automatischen yq-Download: ${arch}" ;;
  esac

  local binary_name="yq_${os}_${arch}"
  local yq_version
  yq_version="$(read_pinned_version)"
  yq_version="$(printf '%s' "${yq_version}" | sed "s/['\"]//g")"
  if [[ "${yq_version}" != v* ]]; then
    yq_version="v${yq_version}"
  fi

  local url="https://github.com/mikefarah/yq/releases/download/${yq_version}/${binary_name}"
  local checksum_base="https://github.com/mikefarah/yq/releases/download/${yq_version}"

  if [[ "${DRY_RUN:-}" = "1" ]]; then
    echo "${url}"
    return 0
  fi

  # If a correct local binary already exists, do nothing.
  if [[ -x "${YQ_LOCAL}" ]]; then
    local existing_version=""
    existing_version="$("${YQ_LOCAL}" --version 2> /dev/null | sed -E 's/^yq .* version //' || echo "")"
    if [[ -n "${existing_version}" ]] && version_ok "${existing_version}" "${yq_version}"; then
      log "Existing ${YQ_LOCAL} already has correct version ${existing_version}, skipping download"
      return 0
    fi
    log "Removing incompatible yq binary (version ${existing_version:-unknown})"
    rm -f "${YQ_LOCAL}"
  fi

  local tmp tmp_checksum
  tmp="$(mktemp "${YQ_LOCAL}.dl.XXXXXX")"
  tmp_checksum="$(mktemp "${YQ_LOCAL}.sha256.XXXXXX")"
  trap 'rm -f -- "${tmp-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

  log "Probiere Download-URL für ${yq_version}: ${url}"
  log "Binary name: ${binary_name}, OS: ${os}, Arch: ${arch}"

  if ! curl --fail --max-time 60 --connect-timeout 10 --retry 3 -fsSL "${url}" -o "${tmp}"; then
    die "Download von yq fehlgeschlagen: ${url}"
  fi

  # Checksums (best effort)
  local checksum_asset=""
  local checksum_url=""
  local checksum_candidates=(
    "checksums"
    "checksums.txt"
    "checksums-bsd"
    "${binary_name}.sha256"
    "${binary_name}.sha256.txt"
  )

  rm -f -- "${tmp_checksum}" || true
  for candidate in "${checksum_candidates[@]}"; do
    checksum_url="${checksum_base}/${candidate}"
    log "Probiere Checksummen-Datei: ${checksum_url}"
    if curl --fail --max-time 60 --connect-timeout 10 --retry 3 -fsSL "${checksum_url}" -o "${tmp_checksum}"; then
      if [[ -s "${tmp_checksum}" ]]; then
        checksum_asset="${candidate}"
        log "Gefundene Checksummen-Datei: ${checksum_asset} ($(wc -l < "${tmp_checksum}") Zeilen)"
        break
      else
        log "WARN: Checksummen-Datei ${candidate} ist leer, versuche nächste..."
        rm -f -- "${tmp_checksum}"
      fi
    fi
  done

  if [[ -n "${checksum_asset}" ]]; then
    log "Verifiziere Checksumme aus ${checksum_asset}..."
    local expected_sum=""

    if [[ "${checksum_asset}" == "checksums" || "${checksum_asset}" == "checksums.txt" || "${checksum_asset}" == "checksums-bsd" ]]; then
      local checksum_line
      checksum_line="$(grep "^${binary_name}[[:space:]]" "${tmp_checksum}" | head -n1 || true)"
      if [[ -n "${checksum_line}" ]]; then
        local my_sum=""
        if command -v sha256sum > /dev/null 2>&1; then
          my_sum="$(sha256sum "${tmp}" | awk '{print $1}')"
        elif command -v shasum > /dev/null 2>&1; then
          my_sum="$(shasum -a 256 "${tmp}" | awk '{print $1}')"
        elif command -v python3 > /dev/null 2>&1; then
          my_sum="$(python3 -c "import hashlib; print(hashlib.sha256(open('${tmp}','rb').read()).hexdigest())")"
        elif command -v python > /dev/null 2>&1; then
          my_sum="$(python -c "import hashlib; print(hashlib.sha256(open('${tmp}','rb').read()).hexdigest())")"
        fi

        if [[ -n "${my_sum}" ]] && echo "${checksum_line}" | grep -q "${my_sum}"; then
          expected_sum="${my_sum}"
        else
          log "WARN: Multi-Column-Checksumme konnte nicht sicher validiert werden, überspringe Verifikation."
        fi
      fi
    else
      local checksum_line
      checksum_line="$(grep -E "^[a-fA-F0-9]{64}[[:space:]]+${binary_name}([[:space:]]+.*)?$" "${tmp_checksum}" || true)"
      if [[ -n "${checksum_line}" ]]; then
        expected_sum="$(echo "${checksum_line}" | awk '{print $1}')"
      fi
    fi

    if [[ -n "${expected_sum}" ]]; then
      local actual_sum=""
      if command -v sha256sum > /dev/null 2>&1; then
        actual_sum="$(sha256sum "${tmp}" | awk '{print $1}')"
      elif command -v shasum > /dev/null 2>&1; then
        actual_sum="$(shasum -a 256 "${tmp}" | awk '{print $1}')"
      elif command -v python3 > /dev/null 2>&1; then
        actual_sum="$(python3 -c "import hashlib; print(hashlib.sha256(open('${tmp}','rb').read()).hexdigest())")"
      elif command -v python > /dev/null 2>&1; then
        actual_sum="$(python -c "import hashlib; print(hashlib.sha256(open('${tmp}','rb').read()).hexdigest())")"
      fi

      if [[ -n "${actual_sum}" && "${expected_sum}" != "${actual_sum}" ]]; then
        die "Checksum-Verifikation fehlgeschlagen! Erwartet: ${expected_sum}, Ist: ${actual_sum} (Quelle: ${checksum_asset})"
      fi
      log "Checksumme ok (Quelle ${checksum_asset}): ${actual_sum:-unverified}"
    else
      log "WARN: Keine passende SHA256-Checksumme gefunden – Verifikation übersprungen."
    fi
  else
    log "WARN: Keine Checksummen-Datei im Release gefunden, überspringe Verifikation."
  fi

  chmod +x "${tmp}" || true
  mv -f -- "${tmp}" "${YQ_LOCAL}"
  chmod +x "${YQ_LOCAL}"

  "${YQ_LOCAL}" --version > /dev/null 2>&1 || die "Heruntergeladenes yq-Binary ist nicht ausführbar oder defekt."
  log "yq erfolgreich nach ${YQ_LOCAL} heruntergeladen."
}

resolved_yq() {
  if [[ -x "${YQ_LOCAL}" ]]; then
    echo "${YQ_LOCAL}"
    return 0
  fi
  if have_cmd yq; then
    command -v yq
    return 0
  fi
  return 1
}

cmd_ensure() {
  ensure_dir
  local pinned_version
  pinned_version="$(read_pinned_version)"

  # Lokales BIN_DIR für diesen Aufruf priorisieren
  export PATH="${BIN_DIR}:${PATH}"

  local yq_bin=""
  local v=""
  local version_is_ok=false

  if yq_bin="$(resolved_yq)"; then
    log "Benutze yq-Binary unter ${yq_bin}"
    v="$("${yq_bin}" --version 2> /dev/null | sed -E 's/^yq .* version v?//')"
    if version_ok "${v}" "${pinned_version}"; then
      version_is_ok=true
    else
      log "WARN: Found yq is wrong version: ${v} (erwartet: ${pinned_version})"
    fi
  fi

  if ! ${version_is_ok}; then
    download_yq
    [[ "${DRY_RUN:-}" = "1" ]] && return 0
    yq_bin="$(resolved_yq)" || die "yq nach Download immer noch nicht gefunden."
    v="$("${yq_bin}" --version 2> /dev/null | sed -E 's/^yq .* version v?//')" || die "konnte yq-Version nach Download nicht ermitteln"
    version_ok "${v}" "${pinned_version}" || die "Heruntergeladenes yq hat falsche Version: ${v} (erwartet: ${pinned_version})"
  fi

  if [[ "${yq_bin}" != "${YQ_LOCAL}" && ! -e "${YQ_LOCAL}" ]]; then
    ln -s -- "${yq_bin}" "${YQ_LOCAL}" || true
  fi
  log "OK: yq ${v} verfügbar"
}

case "${1:-ensure}" in
  ensure) cmd_ensure "$@" ;;
  *) die "usage: $0 ensure" ;;
esac
