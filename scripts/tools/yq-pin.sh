#!/usr/bin/env bash
set -euxo pipefail
# Pin & Ensure für mikefarah/yq v4.x – standardmäßig offline zur Laufzeit.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/yq liegt oder im PATH verfügbar ist.
# Optionaler Download ist NUR erlaubt, wenn ALLOW_NET=1 gesetzt ist.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
YQ_LOCAL="${BIN_DIR}/yq"

# Source centralized semver and installer libraries
# shellcheck source=scripts/lib/semver.sh
source "${ROOT_DIR}/scripts/lib/semver.sh"
# shellcheck source=scripts/lib/installer.bash
source "${ROOT_DIR}/scripts/lib/installer.bash"

# Override read_pinned_version to add specific yq prefix handling if needed,
# or just use the generic one.
# yq-pin.sh previously didn't support YQ_VERSION env override, but we can add it or just stick to file.
# The original script strictly read from file. We'll stick to that for now to avoid behavior change.
read_pinned_version() {
  local v
  v="$(read_toolchain_version "yq" "${ROOT_DIR}/toolchain.versions.yml")"
  if [[ -z "${v}" ]]; then
     die "Konnte gewünschte yq-Version aus toolchain.versions.yml nicht ermitteln."
  fi
  printf '%s' "${v}"
}

download_yq() {
  # Default: OFFLINE. Download only when explicitly allowed.
  if [[ "${ALLOW_NET:-}" != "1" ]]; then
    die "yq fehlt/inkompatibel und Download ist deaktiviert. Setze ALLOW_NET=1, oder lege ein gepinntes Binary nach ${YQ_LOCAL}."
  fi

  ensure_dir "${BIN_DIR}"
  log "yq nicht gefunden/inkompatibel. Download ist erlaubt (ALLOW_NET=1)."

  require_cmd curl "Bitte curl installieren oder in PATH bereitstellen."

  local os
  os="$(detect_os_normalized)"

  local arch
  arch="$(detect_arch_normalized)"
  # Map generic arch to yq specific naming (x86_64 -> amd64)
  if [[ "${arch}" == "x86_64" ]]; then arch="amd64"; fi
  if [[ "${arch}" == "aarch64" ]]; then arch="arm64"; fi

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

  if ! download_file "${url}" "${tmp}"; then
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
    if download_file "${checksum_url}" "${tmp_checksum}" > /dev/null 2>&1; then
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
        my_sum="$(calculate_sha256 "${tmp}")"

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
      actual_sum="$(calculate_sha256 "${tmp}")"

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
  ensure_dir "${BIN_DIR}"
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
