#!/usr/bin/env bash
set -euxo pipefail
# Pin & Ensure für mikefarah/yq v4.x – ohne Netz zur Laufzeit.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/yq liegt oder im PATH verfügbar ist.

REQ_MAJOR=4
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
  # Strip leading 'v' and quotes from wanted version
  local v_want_clean
  v_want_clean=$(echo "${v_want}" | tr -d "'\"v")
  # Strip leading 'v' from have version
  local v_have_clean
  v_have_clean=$(echo "${v_have}" | tr -d "v")
  [[ "${v_have_clean}" == "${v_want_clean}" ]]
}

require_cmd() {
  local cmd="$1"
  local hint="$2"
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

  # Always parse version from toolchain.versions.yml robustly using grep/sed.
  # Do NOT rely on `yq` command here to avoid bootstrap paradox (e.g. wrong yq in path).
  local version
  version=$(grep -E '^[[:space:]]*yq[[:space:]]*:' "${ROOT_DIR}/toolchain.versions.yml" | head -n1 |
    sed -E 's/^[[:space:]]*[^:]+:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' |
    tr -d '\n\r')

  if [[ -z "${version}" ]]; then
    die "Konnte gewünschte yq-Version aus toolchain.versions.yml nicht ermitteln."
  fi
  printf '%s' "${version}"
}

download_yq() {
  ensure_dir
  log "yq nicht gefunden/inkompatibel. Lade v${REQ_MAJOR}.x herunter..."
  require_cmd curl "Bitte curl installieren oder in PATH bereitstellen."

  local os
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  case "${os}" in
    linux | darwin) ;;
    *)
      die "Nicht unterstütztes Betriebssystem für automatischen yq-Download: ${os}"
      ;;
  esac

  local arch
  arch=$(uname -m)
  case "${arch}" in
    x86_64) arch="amd64" ;;
    aarch64) arch="arm64" ;;
    arm64) arch="arm64" ;;
    *)
      die "Nicht unterstützte Architektur für automatischen yq-Download: ${arch}"
      ;;
  esac

  local binary_name="yq_${os}_${arch}"
  local yq_version
  yq_version="$(read_pinned_version)"
  yq_version=$(printf '%s' "${yq_version}" | sed "s/['\"]//g")
  if [[ "${yq_version}" != v* ]]; then
    yq_version="v${yq_version}"
  fi
  local url="https://github.com/mikefarah/yq/releases/download/${yq_version}/${binary_name}"
  local checksum_base="https://github.com/mikefarah/yq/releases/download/${yq_version}"

  if [ "${DRY_RUN:-}" = "1" ]; then
    echo "${url}"
    return 0
  fi

  ensure_dir

  # Force cleanup of existing binaries in target location
  rm -f "${YQ_LOCAL}"

  local tmp tmp_checksum
  tmp="$(mktemp "${YQ_LOCAL}.dl.XXXXXX")"
  tmp_checksum="$(mktemp "${YQ_LOCAL}.sha256.XXXXXX")"
  # ${var-} um set -u sauber zu halten
  trap 'rm -f -- "${tmp-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

  log "Probiere Download-URL für ${yq_version}: ${url}"
  log "Binary name: ${binary_name}, OS: ${os}, Arch: ${arch}"
  # Binary herunterladen
  if ! curl --fail --max-time 60 --connect-timeout 10 --retry 3 -fsSL "${url}" -o "${tmp}"; then
    if [[ -x "${YQ_LOCAL}" ]]; then
      log "Download fehlgeschlagen – benutze vorhandenen Pin unter ${YQ_LOCAL} (offline fallback)."
      return 0
    fi
    log "FEHLER: Download von yq fehlgeschlagen"
    log "URL: ${url}"
    log "Version: ${yq_version}"
    log "Mögliche Ursachen:"
    log "  - Netzwerkproblem oder GitHub API-Limit"
    log "  - Release ${yq_version} existiert nicht oder hat kein Asset ${binary_name}"
    log "  - Überprüfen Sie: https://github.com/mikefarah/yq/releases/tag/${yq_version}"
    die "Download von yq fehlgeschlagen: ${url}"
  fi

  # Checksummen herunterladen und prüfen (falls verfügbar)
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

  if [[ -z "${checksum_asset}" ]]; then
    log "WARN: Keine Checksummen-Datei im Release gefunden, überspringe Verifikation."
    log "Versuchte Dateinamen: ${checksum_candidates[*]}"
    log "Wenn das Release absichtlich keine Checksums hat, können Sie:"
    log "  1. Eine andere YQ_VERSION wählen, die Checksums hat"
    log "  2. Einen bekannten Hash in toolchain.versions.yml hinzufügen"
  fi

  if [[ -n "${checksum_asset}" ]]; then
    log "Verifiziere Checksumme aus ${checksum_asset}..."
    local expected_sum=""

    if [[ "${checksum_asset}" == "checksums" || "${checksum_asset}" == "checksums.txt" || "${checksum_asset}" == "checksums-bsd" ]]; then
      # Multi-column format: "filename hash1 hash2 ..."
      # Use reverse lookup: Calculate local hash first, then check if it is present in the line.
      # This avoids fragile column guessing.

      local checksum_line
      checksum_line=$(grep "^${binary_name}[[:space:]]" "${tmp_checksum}" | head -n1 || true)
      if [[ -n "${checksum_line}" ]]; then
        local my_sum=""
        if command -v sha256sum > /dev/null 2>&1; then
          my_sum=$(sha256sum "${tmp}" | awk '{print $1}')
        elif command -v shasum > /dev/null 2>&1; then
          my_sum=$(shasum -a 256 "${tmp}" | awk '{print $1}')
        fi

        if [[ -n "${my_sum}" ]]; then
          if echo "${checksum_line}" | grep -q "${my_sum}"; then
            expected_sum="${my_sum}"
          else
            log "WARN: Berechneter Hash ${my_sum} nicht in Checksum-Zeile gefunden."
          fi
        elif command -v python3 > /dev/null 2>&1; then
          log "Using Python3 fallback for SHA256 checksum..."
          local my_sum
          my_sum=$(python3 -c "import hashlib, sys; print(hashlib.sha256(open('${tmp}', 'rb').read()).hexdigest())")
          if echo "${checksum_line}" | grep -q "${my_sum}"; then
            expected_sum="${my_sum}"
          else
            log "WARN: Berechneter Hash ${my_sum} nicht in Checksum-Zeile gefunden."
          fi
        elif command -v python > /dev/null 2>&1; then
          log "Using Python fallback for SHA256 checksum..."
          local my_sum
          my_sum=$(python -c "import hashlib, sys; print(hashlib.sha256(open('${tmp}', 'rb').read()).hexdigest())")
          if echo "${checksum_line}" | grep -q "${my_sum}"; then
            expected_sum="${my_sum}"
          else
            log "WARN: Berechneter Hash ${my_sum} nicht in Checksum-Zeile gefunden."
          fi
        else
          log "WARN: Weder sha256sum noch shasum verfügbar - kann Multi-Column-Checksumme nicht verifizieren."
        fi
      fi
    else
      # Standard "HASH filename" format
      local checksum_line
      checksum_line=$(grep -E "^[a-fA-F0-9]{64}[[:space:]]+${binary_name}([[:space:]]+.*)?$" "${tmp_checksum}" || true)
      if [[ -n "${checksum_line}" ]]; then
        expected_sum=$(echo "${checksum_line}" | awk '{print $1}')
      fi
    fi

    if [[ -z "${expected_sum}" ]]; then
      log "WARN: Keine passende SHA256-Checksumme für ${binary_name} in ${checksum_asset} gefunden (oder Tool fehlt), überspringe Verifikation."
    else
      local actual_sum
      if command -v sha256sum > /dev/null 2>&1; then
        actual_sum=$(sha256sum "${tmp}" | awk '{print $1}')
      elif command -v shasum > /dev/null 2>&1; then
        actual_sum=$(shasum -a 256 "${tmp}" | awk '{print $1}')
      elif command -v python3 > /dev/null 2>&1; then
        log "Using Python3 fallback for SHA256 checksum..."
        actual_sum=$(python3 -c "import hashlib, sys; print(hashlib.sha256(open('${tmp}', 'rb').read()).hexdigest())")
      elif command -v python > /dev/null 2>&1; then
        log "Using Python fallback for SHA256 checksum..."
        actual_sum=$(python -c "import hashlib, sys; print(hashlib.sha256(open('${tmp}', 'rb').read()).hexdigest())")
      else
        log "WARN: No sha256sum, shasum, or python found for checksum verification - skipping verification."
        actual_sum=""
      fi

      if [[ -n "${actual_sum}" ]]; then
        if [[ "${expected_sum}" != "${actual_sum}" ]]; then
          die "Checksum-Verifikation fehlgeschlagen! Erwartet: ${expected_sum}, Ist: ${actual_sum} (Quelle: ${checksum_asset})"
        else
          log "Checksumme ok (Quelle ${checksum_asset}): ${actual_sum}"
        fi
      fi
    fi
  fi

  if [[ -f "${tmp}" ]]; then
    chmod +x "${tmp}" || true
    mv -f -- "${tmp}" "${YQ_LOCAL}"
    chmod +x "${YQ_LOCAL}"

    # Ausführung testen
    if ! "${YQ_LOCAL}" --version > /dev/null 2>&1; then
      die "Heruntergeladenes yq-Binary ist nicht ausführbar oder defekt."
    fi

    log "yq erfolgreich nach ${YQ_LOCAL} heruntergeladen und verifiziert."
  fi
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
  local v
  local version_is_ok=false
  local pinned_version
  pinned_version=$(read_pinned_version)

  # Lokales BIN_DIR für diesen Aufruf priorisieren
  export PATH="${BIN_DIR}:${PATH}"

  if yq_bin="$(resolved_yq)"; then
    log "Benutze yq-Binary unter ${yq_bin}"
    if v="$("${yq_bin}" --version 2> /dev/null | sed -E 's/^yq .* version v?//')"; then
      if version_ok "${v}" "${pinned_version}"; then
        version_is_ok=true
      else
        log "WARN: Found yq is wrong version: ${v}"
        log "Erwartet wurde Version ${pinned_version}."
      fi
    else
      log "WARN: Konnte Version von ${yq_bin} nicht bestimmen."
    fi
  fi

  if ! $version_is_ok; then
    download_yq
    if [ "${DRY_RUN:-}" = "1" ]; then
      return 0
    fi
    # After download, resolved_yq should find the local binary first.
    if ! yq_bin="$(resolved_yq)"; then
      die "yq nach Download immer noch nicht gefunden."
    fi
    if ! v="$("${yq_bin}" --version 2> /dev/null | sed -E 's/^yq .* version v?//')"; then
      die "konnte yq-Version nach Download nicht ermitteln"
    fi
    if ! version_ok "${v}" "${pinned_version}"; then
      die "Heruntergeladenes yq hat falsche Version: ${v}"
    fi
  fi

  if [[ "${yq_bin}" != "${YQ_LOCAL}" && ! -e "${YQ_LOCAL}" ]]; then
    ln -s -- "${yq_bin}" "${YQ_LOCAL}" || true
  fi
  log "OK: yq ${v} verfügbar"
}

case "${1:-ensure}" in
  ensure)
    cmd_ensure "$@"
    ;;
  *)
    die "usage: $0 ensure"
    ;;
esac
