#!/usr/bin/env bash
set -euo pipefail
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

have_cmd() { command -v "$1" >/dev/null 2>&1; }

version_ok() {
	local v="$1"
	[[ "$v" =~ ^([0-9]+)\. ]] || return 1
	local major="${BASH_REMATCH[1]}"
	[[ "${major}" -eq "${REQ_MAJOR}" ]]
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
        local version
        if [[ -x "${YQ_LOCAL}" ]]; then
                version=$("${YQ_LOCAL}" '.yq' "${ROOT_DIR}/toolchain.versions.yml" 2>/dev/null || true)
        elif have_cmd yq; then
                version=$(yq '.yq' "${ROOT_DIR}/toolchain.versions.yml" 2>/dev/null || true)
        fi
        if [[ -z "${version}" ]]; then
                version=$(grep -E '^\s*yq:' "${ROOT_DIR}/toolchain.versions.yml" | sed -E 's/^\s*yq:\s*["'\'']?([^"'\'']+)["'\'']?/\1/' | xargs)
        fi
        if [[ -z "${version}" ]]; then
                die "Konnte gewünschte yq-Version aus toolchain.versions.yml nicht ermitteln."
        fi
        printf '%s' "${version}"
}

download_yq() {
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
        local yq_version tag_primary tag_alt
        local yq_version
        yq_version="$(read_pinned_version)"
        yq_version=$(printf '%s' "${yq_version}" | sed "s/['\"]//g")
        if [[ "${yq_version}" != v* ]]; then
                yq_version="v${yq_version}"
        fi
        local url="https://github.com/mikefarah/yq/releases/download/${yq_version}/${binary_name}"

        ensure_dir

        local tmp
        tmp="$(mktemp "${YQ_LOCAL}.dl.XXXXXX")"
        trap 'tmp_file=${tmp-}; if [[ -n "${tmp_file}" ]]; then rm -f -- "${tmp_file}" 2>/dev/null || true; fi' EXIT
        log "Probiere Download-URL für ${yq_version}..."
        if curl -fsSL "${url}" -o "${tmp}"; then
                log "Downloading from ${url}"
        else
                rm -f -- "${tmp}"
                if [[ -x "${YQ_LOCAL}" ]]; then
                        log "Download nicht gefunden – benutze vorhandenen Pin unter ${YQ_LOCAL} (offline fallback)."
                        trap - EXIT
                        return 0
                fi
                trap - EXIT
                die "Download von yq fehlgeschlagen: ${url}"
        fi
        if [[ -f "${tmp}" ]]; then
                chmod +x "${tmp}" || true
                mv -f -- "${tmp}" "${YQ_LOCAL}"
                log "yq erfolgreich nach ${YQ_LOCAL} heruntergeladen."
                trap - EXIT
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
	local yq_bin
	local v
	local version_is_ok=false

        if yq_bin="$(resolved_yq)"; then
                log "Benutze yq-Binary unter ${yq_bin}"
                if v="$("${yq_bin}" --version 2>/dev/null | sed -E 's/^yq .* version v?//')"; then
                        if version_ok "${v}"; then
                                version_is_ok=true
                        else
                                log "WARN: Found yq is wrong version: ${v}"
                                log "Erwartet wurde Hauptversion ${REQ_MAJOR}."
                        fi
                else
                        log "WARN: Konnte Version von ${yq_bin} nicht bestimmen."
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
