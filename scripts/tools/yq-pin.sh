#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure für mikefarah/yq v4.x – ohne Netz zur Laufzeit.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/yq liegt oder im PATH verfügbar ist.

REQ_MAJOR=4
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
YQ_LOCAL="${BIN_DIR}/yq"

log(){ printf '%s\n' "$*" >&2; }
die(){ log "ERR: $*"; exit 1; }

ensure_dir(){ mkdir -p -- "${BIN_DIR}"; }

have_cmd(){ command -v "$1" >/dev/null 2>&1; }

version_ok(){
  local v="$1"
  [[ "$v" =~ ^([0-9]+)\. ]] || return 1
  local major="${BASH_REMATCH[1]}"
  [[ "${major}" -eq "${REQ_MAJOR}" ]]
}

download_yq() {
  log "yq nicht gefunden/inkompatibel. Lade v${REQ_MAJOR}.x herunter..."
  local os
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  local arch
  arch=$(uname -m)
  case "${arch}" in
    x86_64) arch="amd64" ;;
    aarch64) arch="arm64" ;;
  esac

  local binary_name="yq_${os}_${arch}"
  local yq_version
  # We need yq to read the yq version, so we prefer the local pin if it exists,
  # otherwise we try the system yq.
  if [[ -x "${YQ_LOCAL}" ]]; then
    yq_version=$("${YQ_LOCAL}" '.yq' "${ROOT_DIR}/toolchain.versions.yml")
  elif have_cmd yq; then
    yq_version=$(yq '.yq' "${ROOT_DIR}/toolchain.versions.yml")
  else
    # As a last resort, try to parse with grep. This is not robust, but it's
    # better than nothing.
    yq_version=$(grep -E '^\s*yq:' "${ROOT_DIR}/toolchain.versions.yml" | sed -E 's/^\s*yq:\s*["'\'']?([^"'\'']+)["'\'']?/\1/' | xargs)
  fi
  local yq_url="https://github.com/mikefarah/yq/releases/download/${yq_version}/${binary_name}"

  ensure_dir

  local tmp
  tmp="$(mktemp "${YQ_LOCAL}.dl.XXXXXX")"
  log "Downloading from ${yq_url}"
  if curl -fSL "${yq_url}" -o "${tmp}"; then
    chmod +x "${tmp}" || true
    mv -f -- "${tmp}" "${YQ_LOCAL}"
    log "yq erfolgreich nach ${YQ_LOCAL} heruntergeladen."
  else
    rm -f -- "${tmp}"
    if [[ -x "${YQ_LOCAL}" ]]; then
      log "Download fehlgeschlagen – benutze vorhandenen Pin unter ${YQ_LOCAL} (offline fallback)."
    else
      die "Download von yq fehlgeschlagen und kein nutzbarer Pin vorhanden."
    fi
  fi
}

resolved_yq(){
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

cmd_ensure(){
  ensure_dir
  local yq_bin
  local v
  local version_is_ok=false

  if yq_bin="$(resolved_yq)"; then
    if v="$("${yq_bin}" --version 2>/dev/null | sed -E 's/^yq .* version v?//')"; then
      if version_ok "${v}"; then
        version_is_ok=true
      else
        log "WARN: Found yq is wrong version: ${v}"
      fi
    fi
  fi

  if ! $version_is_ok; then
    download_yq
    # After download, resolved_yq should find the local binary first.
    if ! yq_bin="$(resolved_yq)"; then
      die "yq nach Download immer noch nicht gefunden."
    fi
    if ! v="$("${yq_bin}" --version 2>/dev/null | sed -E 's/^yq .* version v?//')"; then
        die "konnte yq-Version nach Download nicht ermitteln"
    fi
    if ! version_ok "${v}"; then
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
    shift
    cmd_ensure "$@"
    ;;
  *)
    die "usage: $0 ensure"
    ;;
esac
