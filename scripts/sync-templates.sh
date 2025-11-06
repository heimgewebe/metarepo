#!/usr/bin/env bash
# c2b: scripts/sync-templates.sh (ideal)
set -euo pipefail
shopt -s globstar nullglob

red() { printf "\e[31m%s\e[0m\n" "$*"; }
green() { printf "\e[32m%s\e[0m\n" "$*"; }
yellow() { printf "\e[33m%s\e[0m\n" "$*"; }
log() { printf "%s\n" "$*" >&2; }

usage() {
	local default_owner="${GITHUB_OWNER:-heimgewebe}"
	cat <<USG
Usage:
  $0 --pull-from <repo-name>  --pattern "<glob>" [--pattern "..."] [--dry-run]
  $0 --push-to   <repo-name>  --pattern "<glob>" [--pattern "..."] [--dry-run]
  $0 --repos-from <file>      --pattern "<glob>" [--pattern "..."] [--dry-run]
  # Optional Namespace:
  [--owner <org-or-user>] | [--owner-from-env]  (Default: ${default_owner})

Patterns sind relativ zu den Template-Roots:
  - templates/.github/workflows/*.yml
  - templates/Justfile
  - templates/docs/**
  - templates/.wgx/profile.yml
USG
}

# --- Args / Defaults ----------------------------------------------------------
REPO_FROM=""
REPO_TO=""
REPOS_FROM_FILE=""
PATTERNS=()
OWNER="${GITHUB_OWNER:-heimgewebe}"
DRYRUN=0

while [[ $# -gt 0 ]]; do
	case "$1" in
	--pull-from)
		REPO_FROM="$2"
		shift 2
		;;
	--push-to)
		REPO_TO="$2"
		shift 2
		;;
	--repos-from)
		REPOS_FROM_FILE="$2"
		shift 2
		;;
	--pattern)
		PATTERNS+=("$2")
		shift 2
		;;
	--owner)
		OWNER="$2"
		shift 2
		;;
	--owner-from-env)
		OWNER="${GITHUB_OWNER:?Missing GITHUB_OWNER}"
		shift
		;;
	--dry-run)
		DRYRUN=1
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		yellow "Ignoriere unbekanntes Argument: $1"
		shift
		;;
	esac
done

if [[ -n "$REPO_FROM" && ( -n "$REPO_TO" || -n "$REPOS_FROM_FILE") ]]; then
	red "Fehler: --pull-from nicht mit --push-to/--repos-from kombinieren."
	exit 1
fi

if [[ -z "$REPO_FROM" && -z "$REPO_TO" && -z "$REPOS_FROM_FILE" ]]; then
	red "Fehler: --pull-from, --push-to oder --repos-from angeben."
	usage
	exit 1
fi

if [[ ${#PATTERNS[@]} -eq 0 ]]; then
	PATTERNS=("templates/.github/workflows/*.yml" "templates/Justfile" "templates/docs/**" "templates/.wgx/profile.yml")
fi

# --- Tooling Guards -----------------------------------------------------------
need() { command -v "$1" >/dev/null 2>&1 || {
	red "Fehlt: $1"
	exit 1
}; }
check_tools() {
	need git
	if ! ./scripts/tools/yq-pin.sh ensure >/dev/null 2>&1; then
		red "yq v4 nicht gefunden oder inkompatibel. Bitte ./scripts/tools/yq-pin.sh manuell ausführen."
		exit 1
	fi
}
check_tools

echo "→ OWNER=${OWNER}  DRYRUN=${DRYRUN}"

# --- Tempdir Lifecycle --------------------------------------------------------
TMPDIR="$(mktemp -d)"
cleanup() { [[ -n "${TMPDIR:-}" && -d "$TMPDIR" ]] && rm -rf -- "$TMPDIR"; }
trap cleanup EXIT INT TERM

# --- Helpers -----------------------------------------------------------------
sanitize_repo_name() {
	local name="$1"
	[[ "$name" =~ ^[A-Za-z0-9._-]+$ ]] || {
		red "Ungültiger Repository-Name: $name"
		exit 1
	}
}

clone_repo() {
	local name="$1"
	sanitize_repo_name "$name"
	local url="https://github.com/${OWNER}/${name}.git"
	rm -rf -- "${TMPDIR:?}/$name"
	if ! git -c advice.detachedHead=false clone --depth=1 "$url" "$TMPDIR/$name" >/dev/null 2>&1; then
		red "Clone fehlgeschlagen: $url"
		exit 1
	fi
}

# Pull: aus Ziel-Repo ins metarepo/templates spiegeln
copy_into_metarepo_from_repo() {
	local name="$1"
	local src=""
	local repo_root="${TMPDIR}/${name}"
	repo_root="${repo_root%/}/"

	for p in "${PATTERNS[@]}"; do
		case "$p" in
		templates/*) src="${p#templates/}" ;; # „templates/“ im Ziel-Repo existiert nicht → Muster relativ
		*) src="$p" ;;
		esac

		# Alle Treffer im Ziel-Repo (Quelle) einsammeln
		local -a files=()
		mapfile -t files < <(compgen -G -- "${TMPDIR}/${name}/${src}" 2>/dev/null || true)
		[[ ${#files[@]} -eq 0 ]] && continue

		for f in "${files[@]}"; do
			[[ -z "$f" ]] && continue

			# Pfad relativ zum Repo-Root bestimmen
			# `repo_root` has a trailing slash already, so the prefix strip works with
			# standard quoting and keeps ShellCheck SC2295 satisfied.
			local rel_f="${f#"${repo_root}"}"
			[[ -z "$rel_f" || "$rel_f" == "$f" ]] && continue

			local dest="$PWD/templates/$rel_f"
			if ((DRYRUN == 1)); then
				echo "↑ (dry-run) Pull: ${name} :: ${rel_f} → templates/${rel_f}"
				continue
			fi
			mkdir -p "$(dirname "$dest")"
			cp -a "$f" "$dest"
			git add "templates/$rel_f" || true
			echo "↑ Pull: ${name} :: ${rel_f} → templates/${rel_f}"
		done
	done
}

# Push: aus metarepo/templates in Ziel-Repo spiegeln
copy_from_metarepo_into_repo() {
	local name="$1"
	local src=""
	local -a files=()
	for p in "${PATTERNS[@]}"; do
		case "$p" in
		templates/*) src="$p" ;;
		*) src="$p" ;;
		esac
		files=()
		mapfile -t files < <(compgen -G -- "$src" 2>/dev/null || true)
		for f in "${files[@]}"; do
			[[ -z "$f" ]] && continue
			local rel="${f#templates/}"
			if [[ "$f" == "$rel" ]]; then
				yellow "Überspringe Nicht-Template: $f"
				continue
			fi
			if ((DRYRUN == 1)); then
				echo "↓ (dry-run) Push: templates/${rel} → ${name}::${rel}"
				continue
			fi
			mkdir -p "$TMPDIR/$name/$(dirname "$rel")"
			cp -a "$f" "$TMPDIR/$name/$rel"
			echo "↓ Push: templates/${rel} → ${name}::${rel}"
		done
	done
	(
		cd "$TMPDIR/$name"
		if ! git diff --quiet; then
			if ((DRYRUN == 1)); then
				echo "DRY-RUN: Änderungen erkannt für $name (kein Commit erstellt)."
			else
				git config user.email "codex-bot@local"
				git config user.name "Codex Bot"
				git checkout -b chore/template-sync || true
				git add .
				git commit -m "chore(templates): sync from metarepo"
				echo "Lokaler Commit erstellt. Bitte PR manuell auf GitHub öffnen."
			fi
		else
			echo "Keine Änderungen für $name."
		fi
	)
}

sync_repos_from_file() {
	local file="$1"
	[[ -f "$file" ]] || {
		red "Repos-Datei nicht gefunden: $file"
		exit 1
	}
	mapfile -t REPOS < <(
		yq -r '
      def to_obj:
        if type == "string" then {name: .}
        elif has("name") then .
        else empty
        end;
      [ (.repos[]? | to_obj), (.static.include[]? | to_obj) ]
      | flatten
      | unique_by(.name)
      | .[].name
    ' "$file"
	)
	if [[ ${#REPOS[@]} -eq 0 ]]; then
		yellow "Keine Repos in $file gefunden (erwartet unter repos:[]/static.include[] mit name-Feld)."
		exit 1
	fi
	for repo in "${REPOS[@]}"; do
		[[ -z "$repo" ]] && continue
		echo "== Sync to $repo =="
		clone_repo "$repo"
		copy_from_metarepo_into_repo "$repo"
	done
}

# --- Entry Points -------------------------------------------------------------
if [[ -n "$REPO_FROM" ]]; then
	clone_repo "$REPO_FROM"
	copy_into_metarepo_from_repo "$REPO_FROM"
	echo "Empfehlung: git commit -m \"chore(templates): pull from $REPO_FROM\""
	exit 0
fi

if [[ -n "$REPOS_FROM_FILE" ]]; then
	sync_repos_from_file "$REPOS_FROM_FILE"
	exit 0
fi

if [[ -n "$REPO_TO" ]]; then
	clone_repo "$REPO_TO"
	copy_from_metarepo_into_repo "$REPO_TO"
	echo "Hinweis: PR für $REPO_TO auf GitHub erstellen (chore/template-sync)."
	exit 0
fi
