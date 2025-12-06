#!/usr/bin/env bash
set -euo pipefail

#
# contracts-sync.sh
#
# Synchronisiert zentrale Contracts aus dem metarepo in ausgewählte
# Domain-Repos. Ziel: Drift zwischen Quelle (`metarepo/contracts`) und
# Kopien vermeiden.
#
# Verwendungsmodi:
#   1) Sync (Standard):
#        ./scripts/contracts-sync.sh
#      → Kopiert alle konfigurierten Contracts in die Ziel-Repos.
#
#   2) Check-Modus (nur vergleichen, nichts schreiben):
#        ./scripts/contracts-sync.sh --check
#      → schlägt mit Exit-Code 1 fehl, falls eine Kopie von der Quelle abweicht
#        oder fehlt.
#
# Annahmen:
#   - Dieses Script wird aus dem `metarepo` aufgerufen.
#   - Die anderen Repos liegen als Geschwister im gleichen Verzeichnis, z. B.:
#       /pfad/zum/arbeitsbaum/
#         metarepo/
#         aussensensor/
#         chronik/
#         ...
#   - Optional kann HEIMGEWEBE_ROOT gesetzt werden, um das gemeinsame Wurzel-
#     verzeichnis explizit zu definieren.
#

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
METAREPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HEIMGEWEBE_ROOT="${HEIMGEWEBE_ROOT:-"$(cd "$METAREPO_ROOT/.." && pwd)"}"

MODE="sync"
if [[ "${1:-}" == "--check" ]]; then
  MODE="check"
  shift || true
fi

if [[ $# -gt 0 ]]; then
  echo "Unbekannte Argumente: $*" >&2
  echo "Usage: $0 [--check]" >&2
  exit 1
fi

log() {
  printf '[contracts-sync] %s\n' "$*" >&2
}

fail() {
  printf '[contracts-sync] ERROR: %s\n' "$*" >&2
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || fail "benötigtes Programm fehlt: $1"
}

need diff

# Mapping: zentrale Contract-Datei → Liste von Zielpfaden in anderen Repos.
# Syntax:
#   "<relativer/pfad/von/metarepo/contracts>" -> "repo1:rel/pfad repo2:anderer/pfad"
#
# Hinweis:
#   - Diese Liste ist bewusst klein gehalten und kann iterativ erweitert werden.
#   - Neue Contracts / Ziel-Repos werden hier eingetragen.

declare -A CONTRACT_TARGETS=()

# Beispiel: aussen.event.schema.json
CONTRACT_TARGETS["contracts/aussen.event.schema.json"]="
  aussensensor:contracts/aussen.event.schema.json
  chronik:docs/aussen.event.schema.json
"

# Weitere Contracts können hier ergänzt werden, z. B.:
# CONTRACT_TARGETS["contracts/heimlern.policy.snapshot.schema.json"]="
#   heimlern:contracts/heimlern.policy.snapshot.schema.json
# "


sync_one_target() {
  local src_rel="$1"
  local target_spec="$2"

  local repo="${target_spec%%:*}"
  local rel_path="${target_spec#*:}"

  local src="$METAREPO_ROOT/$src_rel"
  local dst_repo_root="$HEIMGEWEBE_ROOT/$repo"
  local dst="$dst_repo_root/$rel_path"

  if [[ ! -f "$src" ]]; then
    fail "Quelle nicht gefunden: $src_rel ($src)"
  fi

  if [[ ! -d "$dst_repo_root/.git" ]]; then
    log "Ziel-Repo fehlt oder kein Git-Repo: $dst_repo_root – überspringe"
    return 0
  fi

  if [[ "$MODE" == "check" ]]; then
    if [[ ! -f "$dst" ]]; then
      printf '[contracts-sync] DRIFT: %s fehlt in %s\n' "$rel_path" "$repo" >&2
      return 1
    fi
    if ! diff -q "$src" "$dst" >/dev/null 2>&1; then
      printf '[contracts-sync] DRIFT: %s unterscheidet sich in %s\n' "$rel_path" "$repo" >&2
      return 1
    fi
    return 0
  fi

  mkdir -p "$(dirname "$dst")"
  cp -f "$src" "$dst"
  log "Sync: $src_rel → $repo/$rel_path"
}

main() {
  local overall_status=0

  for src_rel in "${!CONTRACT_TARGETS[@]}"; do
    # Shell-Word-Splitting bewusst, da die Value-Liste whitespace-separiert ist.
    # shellcheck disable=SC2206
    local targets=( ${CONTRACT_TARGETS[$src_rel]} )

    for spec in "${targets[@]}"; do
      if ! sync_one_target "$src_rel" "$spec"; then
        overall_status=1
      fi
    done
  done

  if [[ "$MODE" == "check" ]]; then
    if [[ $overall_status -eq 0 ]]; then
      log "Check: alle Contract-Kopien sind synchron."
    else
      log "Check: es existiert Drift zwischen Quelle und mindestens einem Ziel."
    fi
  fi

  return "$overall_status"
}

main "$@"
