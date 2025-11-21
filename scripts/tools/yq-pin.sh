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

have_cmd() { command -v "$1" >/dev/null 2>&1; }

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
        local checksum_url="${url}.sha256"

        ensure_dir

        # Force cleanup of existing binaries in target location
        rm -f "${YQ_LOCAL}"

        local tmp tmp_checksum
        tmp="$(mktemp "${YQ_LOCAL}.dl.XXXXXX")"
        tmp_checksum="$(mktemp "${YQ_LOCAL}.sha256.XXXXXX")"
        # Use ${var-} expansion to avoid "unbound variable" errors if trap triggers before assignment
        trap 'rm -f -- "${tmp-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

        log "Probiere Download-URL für ${yq_version}: ${url}"

        # Download binary
        if ! curl -fsSL "${url}" -o "${tmp}"; then
                if [[ -x "${YQ_LOCAL}" ]]; then
                        log "Download nicht gefunden – benutze vorhandenen Pin unter ${YQ_LOCAL} (offline fallback)."
                        return 0
                fi
                die "Download von yq fehlgeschlagen: ${url}"
        fi

        # Download checksum
        if curl -fsSL "${checksum_url}" -o "${tmp_checksum}"; then
             log "Verifying checksum..."
             # yq checksum files often contain "filename hash", we need to check against our tmp file
             # But since the filename in the sum file won't match our tmp file, we can just compare the hash manually.
             local expected_sum
             expected_sum=$(awk '{print $19}' "${tmp_checksum}" 2>/dev/null || awk '{print $1}' "${tmp_checksum}")
             local actual_sum
             actual_sum=$(sha256sum "${tmp}" | awk '{print $1}')

             if [[ "${expected_sum}" != "${actual_sum}" ]]; then
                 die "Checksum verification failed! Expected: ${expected_sum}, Actual: ${actual_sum}"
             else
                 log "Checksum verified: ${actual_sum}"
             fi
        else
             log "WARN: No checksum file found at ${checksum_url}, skipping verification."
        fi

        if [[ -f "${tmp}" ]]; then
                chmod +x "${tmp}" || true
                mv -f -- "${tmp}" "${YQ_LOCAL}"
                chmod +x "${YQ_LOCAL}"

                # Verify execution
                if ! "${YQ_LOCAL}" --version >/dev/null; then
                    die "Heruntergeladenes yq Binary ist nicht ausführbar oder defekt."
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

    # Prioritize local BIN_DIR in PATH for this script execution
    export PATH="${BIN_DIR}:${PATH}"

	if yq_bin="$(resolved_yq)"; then
		log "Benutze yq-Binary unter ${yq_bin}"
		if v="$("${yq_bin}" --version 2>/dev/null | sed -E 's/^yq .* version v?//')"; then
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
        # Explicitly use the local binary for verification
        yq_bin="${YQ_LOCAL}"

		if ! v="$("${yq_bin}" --version 2>/dev/null | sed -E 's/^yq .* version v?//')"; then
			die "konnte yq-Version nach Download nicht ermitteln"
		fi
		if ! version_ok "${v}" "${pinned_version}"; then
			die "Heruntergeladenes yq hat falsche Version: ${v}"
		fi
	fi

    # Ensure symlink exists if we are using a different binary (unlikely now due to forced download)
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
