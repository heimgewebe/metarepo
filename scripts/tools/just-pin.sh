#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure für casey/just – ohne Netz zur Laufzeit.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/just liegt oder im PATH verfügbar ist.

REQ_VERSION="1.14.0"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
JUST_LOCAL="${BIN_DIR}/just"

log(){ printf '%s\n' "$*" >&2; }
die(){ log "ERR: $*"; exit 1; }

ensure_dir(){ mkdir -p -- "${BIN_DIR}"; }

have_cmd(){ command -v "$1" >/dev/null 2>&1; }

version_ok(){
  local v="$1"
  [[ "$v" == "${REQ_VERSION}" ]]
}

download_just() {
  log "just nicht gefunden/inkompatibel. Lade v${REQ_VERSION} herunter..."
  local os
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  local arch
  arch=$(uname -m)
  local target="${arch}-unknown-${os}-musl"
  if [[ "${os}" == "darwin" ]]; then
    target="${arch}-apple-darwin"
  fi

  local just_url="https://github.com/casey/just/releases/download/${REQ_VERSION}/just-${REQ_VERSION}-${target}.tar.gz"

  ensure_dir

  local tmp
  tmp="$(mktemp)"
  log "Downloading from ${just_url}"
  if curl -fSL "${just_url}" -o "${tmp}"; then
    tar -xzf "${tmp}" -C "${BIN_DIR}" just
    chmod +x "${JUST_LOCAL}" || true
    rm -f -- "${tmp}"
    log "just erfolgreich nach ${JUST_LOCAL} heruntergeladen."
  else
    rm -f -- "${tmp}"
    if [[ -x "${JUST_LOCAL}" ]]; then
      log "Download fehlgeschlagen – benutze vorhandenen Pin unter ${JUST_LOCAL} (offline fallback)."
    else
      die "Download von just fehlgeschlagen und kein nutzbarer Pin vorhanden."
    fi
  fi
}

resolved_just(){
  if [[ -x "${JUST_LOCAL}" ]]; then
    echo "${JUST_LOCAL}"
    return 0
  fi
  if have_cmd just; then
    command -v just
    return 0
  fi
  return 1
}

cmd_ensure(){
  ensure_dir
  local just_bin
  local v
  local version_is_ok=false

  if just_bin="$(resolved_just)"; then
    if v="$("${just_bin}" --version 2>/dev/null | cut -d' ' -f2)"; then
      if version_ok "${v}"; then
        version_is_ok=true
      else
        log "WARN: Found just is wrong version: ${v}"
      fi
    fi
  fi

  if ! $version_is_ok; then
    download_just
    if ! just_bin="$(resolved_just)"; then
      die "just nach Download immer noch nicht gefunden."
    fi
    if ! v="$("${just_bin}" --version 2>/dev/null | cut -d' ' -f2)"; then
        die "konnte just-Version nach Download nicht ermitteln"
    fi
    if ! version_ok "${v}"; then
        die "Heruntergeladenes just hat falsche Version: ${v}"
    fi
  fi

  if [[ "${just_bin}" != "${JUST_LOCAL}" && ! -e "${JUST_LOCAL}" ]]; then
    ln -s -- "${just_bin}" "${JUST_LOCAL}" || true
  fi
  log "OK: just ${v} verfügbar"
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
