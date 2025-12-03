#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

ROOT="$(git rev-parse --show-toplevel 2> /dev/null || pwd)"
LOG_DIR="${LOG_DIR:-${ROOT}/.e2e-logs}"
REPORT_DIR="${ROOT}/.hauski-reports"
mkdir -p "${REPORT_DIR}"
mkdir -p "${LOG_DIR}"

STAMP="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
OUT="${REPORT_DIR}/${STAMP}-e2e-aussen-chronik-heimlern.md"

cat > "${OUT}" << 'MD'
# E2E-Report: aussensensor → chronik → heimlern

Dieser Report bündelt die Logs des End-to-End-Laufs (Trocken- und Echtlauf).

## Artefakte
MD

{
  echo ""
  echo "Log-Verzeichnis: \`${LOG_DIR}\`"
  echo ""
} >> "${OUT}"

emit() {
  local title="$1"
  local file="$2"
  if [[ -s "${file}" ]]; then
    # einfache Redaction: offensichtliche Token/Header maskieren (ohne Logikbruch)
    redact() {
      sed -E \
        -e 's/(Authorization: *Bearer +)[A-Za-z0-9._-]+/\1****/g' \
        -e 's/(X-Api-Key: +)[A-Za-z0-9._-]+/\1****/g' \
        -e 's/(token=)[A-Za-z0-9._-]+/\1****/g' \
        -e 's/(CHRONIK_TOKEN=)[^[:space:]]+/\1****/g'
    }
    {
      echo "### ${title}"
      echo ""
      echo '```txt'
      # ANSI-Farbcodes entfernen, auf 5000 Zeilen kappen, offensichtliche Secrets maskieren
      sed -e 's/\x1b\[[0-9;]*m//g' "${file}" |
        tail -n 5000 |
        redact ||
        true
      echo '```'
      echo ""
    } >> "${OUT}"
  fi
}

emit "01 validate.sh" "${LOG_DIR}/01_validate.out"
emit "02 push_chronik (dry)" "${LOG_DIR}/02_push_chronik_dry.out"
emit "03 push_heimlern (dry)" "${LOG_DIR}/03_push_heimlern_dry.out"
emit "04 push_chronik (real)" "${LOG_DIR}/04_push_chronik_real.out"
emit "05 push_heimlern (real)" "${LOG_DIR}/05_push_heimlern_real.out"
emit "Gesamtlog" "${LOG_DIR}/e2e.log"

if command -v realpath > /dev/null 2>&1; then
  abs_path="$(realpath "${OUT}")"
elif command -v readlink > /dev/null 2>&1; then
  abs_path="$(readlink -f "${OUT}" 2> /dev/null || echo "${OUT}")"
else
  abs_path="${OUT}"
fi

#
# Announce the final artifact path (optionally compressed)
# ── If gzip is available and the file is >= 1 MiB, compress and announce *.gz.
#    Otherwise, announce the plain file path.
#
final_path="${abs_path}"
if [[ -f "${OUT}" ]]; then
  # Dateigröße plattformverträglich ermitteln
  _size="$(stat -c%s "${OUT}" 2> /dev/null || stat -f%z "${OUT}" 2> /dev/null || echo 0)"
  if command -v gzip > /dev/null 2>&1 && [[ "${_size}" -ge 1048576 ]]; then
    gzip -f "${OUT}" # löscht "${OUT}", erzeugt "${OUT}.gz"
    final_path="${abs_path}.gz"
  fi
fi
echo "✔ Report: ${final_path}"
