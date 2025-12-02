#!/usr/bin/env bash
set -euo pipefail
# Pin & Ensure für casey/just – robust & sicher.
# Erwartet, dass ein kompatibles Binary entweder in ./tools/bin/just liegt oder im PATH verfügbar ist.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
BIN_DIR="${TOOLS_DIR}/bin"
JUST_LOCAL="${BIN_DIR}/just"

log() { printf '%s\n' "$*" >&2; }
die() {
	log "ERR: $*"
	exit 1
}

ensure_dir() { mkdir -p -- "${BIN_DIR}"; }

have_cmd() { command -v "$1" >/dev/null 2>&1; }

# Parse version from toolchain.versions.yml using simple tools to avoid circular dependency on yq
read_pinned_version() {
	local version
	version=$(grep -E '^\s*just:' "${ROOT_DIR}/toolchain.versions.yml" | sed -E 's/^\s*just:\s*["'\'']?([^"'\'']+)["'\'']?/\1/' | xargs)
	if [[ -z "${version}" ]]; then
		die "Konnte gewünschte just-Version aus toolchain.versions.yml nicht ermitteln."
	fi
	printf '%s' "${version}"
}

version_ok() {
	local v_to_check="$1" # e.g. "1.14.0"
	local req_version_raw="$2" # e.g. "v1.14.0"
	# compare them without the 'v'
	[[ "${v_to_check#v}" == "${req_version_raw#v}" ]]
}

map_arch() {
	case "$(uname -m)" in
	x86_64 | amd64) echo x86_64 ;;
	arm64 | aarch64) echo aarch64 ;;
	*) uname -m ;;
	esac
}

detect_libc() {
	# Linux: default to gnu (glibc); allow override
	if [ -n "${JUST_LIBC:-}" ]; then
		echo "$JUST_LIBC"
	elif [ "$(uname -s | tr '[:upper:]' '[:lower:]')" = "linux" ]; then
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
	os="$(uname -s | tr '[:upper:]' '[:lower:]')"
	arch="$(map_arch)"
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

	log "just nicht gefunden/inkompatibel. Lade ${req_version_raw} herunter..."

	local target
	target="$(compute_target)"
	local filename="just-${ver_numeric}-${target}.tar.gz"
	# Just releases use tags without 'v' (e.g. 1.43.0)
	local tag="${req_version_raw#v}"
	local url="https://github.com/casey/just/releases/download/${tag}/${filename}"
	local checksum_base="https://github.com/casey/just/releases/download/${tag}"

	ensure_dir
	local tmp_bin tmp_checksum
	tmp_bin="$(mktemp)"
	tmp_checksum="$(mktemp)"
	# Safe cleanup
	trap 'rm -f -- "${tmp_bin-}" "${tmp_checksum-}" 2>/dev/null || true' EXIT

	log "Downloading binary from ${url}"
	if ! curl -fSL --retry 3 --connect-timeout 10 "${url}" -o "${tmp_bin}"; then
		die "Download fehlgeschlagen: ${url}"
	fi

	local checksum_candidates=( "checksums.txt" "checksums" "SHA256SUMS" )
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
		# Format: SHA256  filename
		expected_sum=$(grep "${filename}$" "${tmp_checksum}" | awk '{print $1}' || true)

		if [[ -z "${expected_sum}" ]]; then
			log "WARN: Keine Checksumme für ${filename} in Datei gefunden."
		else
			local actual_sum
			if have_cmd sha256sum; then
				actual_sum=$(sha256sum "${tmp_bin}" | awk '{print $1}')
			elif have_cmd shasum; then
				actual_sum=$(shasum -a 256 "${tmp_bin}" | awk '{print $1}')
			else
				die "Weder sha256sum noch shasum verfügbar."
			fi

			if [[ "${expected_sum}" != "${actual_sum}" ]]; then
				die "Checksum-Fehler! Erwartet: ${expected_sum}, Ist: ${actual_sum}"
			fi
			log "Checksumme OK: ${actual_sum}"
		fi
	else
		log "WARN: Konnte keine Checksummen-Datei laden. Überspringe Verifikation."
	fi

	tar -xzf "${tmp_bin}" -C "${BIN_DIR}" just
	chmod +x "${JUST_LOCAL}" || true
	log "just erfolgreich nach ${JUST_LOCAL} installiert."
}

resolved_just() {
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

cmd_ensure() {
	ensure_dir
	local just_bin
	local v
	local version_is_ok=false
	local req_version_raw
	req_version_raw="$(read_pinned_version)"

	# Prioritize local bin
	export PATH="${BIN_DIR}:${PATH}"

	if just_bin="$(resolved_just)"; then
		if v="$("${just_bin}" --version 2>/dev/null | cut -d' ' -f2)"; then
			if version_ok "${v}" "${req_version_raw}"; then
				version_is_ok=true
			else
				log "WARN: Gefundenes just hat falsche Version: ${v} (erwartet: ${req_version_raw})"
			fi
		fi
	fi

	if ! $version_is_ok; then
		download_just
		if ! just_bin="$(resolved_just)"; then
			die "just nach Download nicht verfügbar."
		fi
		# Verify again
		v="$("${just_bin}" --version | cut -d' ' -f2)"
		if ! version_ok "${v}" "${req_version_raw}"; then
			die "Installiertes just hat immer noch falsche Version: ${v}"
		fi
	fi

	# Symlink if needed
	if [[ "${just_bin}" != "${JUST_LOCAL}" && ! -e "${JUST_LOCAL}" ]]; then
		ln -s -- "${just_bin}" "${JUST_LOCAL}" || true
	fi
	log "OK: just ${v} verfügbar."
}

case "${1:-ensure}" in
ensure)
	cmd_ensure "$@"
	;;
*)
	die "usage: $0 ensure"
	;;
esac
