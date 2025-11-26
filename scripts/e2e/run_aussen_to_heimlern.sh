#!/usr/bin/env bash
set -euo pipefail

# End-to-End: aussensensor → chronik → heimlern
#
# Erwartet:
#  - AUSSENSENSOR_DIR: Pfad zum Repo "aussensensor"
#  - CHRONIK_INGEST_URL, CHRONIK_TOKEN
#  - HEIMLERN_INGEST_URL
# Optional:
#  - DRY_RUN=1   (führt nur Trockenläufe aus)
#  - LOG_DIR     (Standard: ./.e2e-logs)
#
# Hinweis: Dieses Skript erwartet, dass aussensensor/scripts/push_chronik.sh
#          existiert. Falls aussensensor noch nicht aktualisiert wurde,
#          muss push_leitstand.sh zu push_chronik.sh umbenannt werden.
#
# Exit-Codes sind streng; bei Fehlern bricht das Script ab.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOG_DIR="${LOG_DIR:-${ROOT}/.e2e-logs}"
mkdir -p "${LOG_DIR}"

ts() { date +"%Y-%m-%d %H:%M:%S"; }
log() { printf "• %s %s\n" "$(ts)" "$*" | tee -a "${LOG_DIR}/e2e.log"; }
ok() { printf "✓ %s %s\n" "$(ts)" "$*" | tee -a "${LOG_DIR}/e2e.log"; }
err() { printf "✗ %s %s\n" "$(ts)" "$*" | tee -a "${LOG_DIR}/e2e.log" >&2; }

[[ -d "${AUSSENSENSOR_DIR:-}" ]] || {
	err "AUSSENSENSOR_DIR fehlt/ungültig"
	exit 2
}
[[ -n "${CHRONIK_INGEST_URL:-}" ]] || {
	err "CHRONIK_INGEST_URL fehlt"
	exit 2
}
[[ -n "${CHRONIK_TOKEN:-}" ]] || {
	err "CHRONIK_TOKEN fehlt"
	exit 2
}
[[ -n "${HEIMLERN_INGEST_URL:-}" ]] || {
	err "HEIMLERN_INGEST_URL fehlt"
	exit 2
}

export CHRONIK_INGEST_URL="${CHRONIK_INGEST_URL}"
export CHRONIK_TOKEN="${CHRONIK_TOKEN}"
export HEIMLERN_INGEST_URL="${HEIMLERN_INGEST_URL}"

AS="${AUSSENSENSOR_DIR}"

log "Starte E2E in ${AS}"
pushd "${AS}" >/dev/null
trap 'popd >/dev/null || true' EXIT

log "Validiere JSONL (aussensensor/scripts/validate.sh)"
if [[ -x scripts/validate.sh ]]; then
	scripts/validate.sh export/feed.jsonl | tee "${LOG_DIR}/01_validate.out"
else
	err "scripts/validate.sh nicht gefunden/ausführbar"
	exit 3
fi
ok "Validierung abgeschlossen"

log "Trockenlauf: push_chronik.sh --dry-run (chronik ingest)"
if [[ -x scripts/push_chronik.sh ]]; then
	scripts/push_chronik.sh --dry-run | tee "${LOG_DIR}/02_push_chronik_dry.out"
else
	err "scripts/push_chronik.sh fehlt"
	exit 3
fi
ok "Trockenlauf zu Chronik ok"

log "Trockenlauf: push_heimlern.sh --dry-run"
if [[ -x scripts/push_heimlern.sh ]]; then
	scripts/push_heimlern.sh --dry-run | tee "${LOG_DIR}/03_push_heimlern_dry.out"
else
	err "scripts/push_heimlern.sh fehlt"
	exit 3
fi
ok "Trockenlauf zu Heimlern ok"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
	ok "DRY_RUN=1 aktiv – beende nach Trockenläufen"
	exit 0
fi

log "REAL: push_chronik.sh (chronik ingest)"
scripts/push_chronik.sh | tee "${LOG_DIR}/04_push_chronik_real.out"
ok "Echtlauf zu Chronik ok"

log "REAL: push_heimlern.sh"
scripts/push_heimlern.sh | tee "${LOG_DIR}/05_push_heimlern_real.out"
ok "Echtlauf zu Heimlern ok"

ok "E2E abgeschlossen"
