export PATH := ".bin:./tools/bin:" + env_var('PATH')

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# --- Devcontainer integration (auto-imported) ---
# erlaubt z. B.:
#   just devcontainer:sync
#   just devcontainer:socket
#   just devcontainer:dind
#   just devcontainer:which
import? ".devcontainer/justfile"
# --- Meta ---------------------------------------------------------------------
default: help

help:
    @printf "Metarepo Justfile – häufige Kommandos:\n"
    @printf "  just deps          # Tooling & Pins via uv sync --frozen\n"
    @printf "  just deps-graph    # Dependency graph (GEXF + JSON unter reports/graphs/)\n"
    @printf "  just list          # WGX-Liste aller angebundenen Repos\n"
    @printf "  just up            # Templates synchronisieren (wgx up)\n"
    @printf "  just validate      # Lokale Checks (Linting, Format, yq)\n"
    @printf "  just smoke         # Schneller Fleet-Integrationslauf\n"
    @printf "  just log-sync      # Report-Vorlage unter reports/sync-logs/\n"
    @printf "  just fleet         # Fleet Readiness & Repos List generieren\n"
    @printf "  just doctor        # Fleet Diagnose (Health Check)\n"
    @printf "\nWeitere Ziele: just --list\n"

# --- Aliase -------------------------------------------------------------------
alias wgx := _wgx
alias yq  := _yq

# --- Org Assets ---------------------------------------------------------------
deps:
    uv sync --frozen

deps-graph:
    @mkdir -p reports/graphs
    @python3 scripts/graph/deps_graph.py \
        --output reports/graphs/deps_graph.gexf \
        --json-output reports/graphs/deps_graph.json

impact-analysis *args:
    @python3 scripts/graph/impact_analysis.py \
        --graph reports/graphs/deps_graph.gexf \
        {{args}}

org-index:
    uv run scripts/generate_org_assets.py --repos-file repos.yml --index docs/org-index.md

org-graph:
    uv run scripts/generate_org_assets.py --repos-file repos.yml --graph docs/org-graph.mmd

linkcheck:
    docker run --rm -v $PWD:/work ghcr.io/lycheeverse/lychee:v0.15.1 \
      --config /work/.lychee.toml

# --- Tasks --------------------------------------------------------------------
# Tooling guards
yq_ensure:
    just _yq ensure

# Fleet-Kommandos
list:
    just _wgx list

up:
    just _wgx up

run target="smoke":
    just _wgx run {{target}}

wgx_validate:
    just _wgx validate

smoke:
    just _wgx smoke

adr-lint:
    @if [ -x tools/adr-lint.sh ]; then \
      tools/adr-lint.sh; \
    else \
      echo "hint: tools/adr-lint.sh fehlt – bitte metarepo-Templates/Scripts aktualisieren." >&2; \
      exit 1; \
    fi

sync:
    scripts/sync-templates.sh

log-sync *args:
    scripts/create-sync-log.py {{args}}

# --- Fleet Utilities (New) -----------------------------------------------------

# Generate fleet readiness report and derived fleet/repos.txt
fleet:
    @echo "→ Generating Heimgewebe fleet readiness and repos list"
    @python scripts/fleet/generate_readiness.py \
        --matrix docs/repo-matrix.md \
        --out-json reports/heimgewebe-readiness.json \
        --write-repos-txt fleet/repos.txt
    @echo "✓ Done. See:"
    @echo "  - reports/heimgewebe-readiness.json"
    @echo "  - fleet/repos.txt"

# Verify that fleet/repos.txt matches generated output exactly
fleet-check:
    @python scripts/fleet/verify_generated_repos_txt.py \
        --matrix docs/repo-matrix.md \
        --fleet fleet/repos.txt

# Diagnose current fleet readiness from reports/heimgewebe-readiness.json
doctor:
    @[ -f reports/heimgewebe-readiness.json ] || just fleet
    @python scripts/fleet/doctor.py --report reports/heimgewebe-readiness.json

# Doctor in CI mode: returns nonzero on WARN/CRITICAL
doctor-ci:
    @[ -f reports/heimgewebe-readiness.json ] || just fleet
    @python scripts/fleet/doctor.py --report reports/heimgewebe-readiness.json --ci

# --- Fleet Push (Wave-1: agent-kit + contracts) --------------------------------
# Voraussetzungen:
#  - GitHub CLI (`gh`) mit Push-Rechten
#  - Python 3.11+
#  - templates/agent-kit/** vorhanden
#  - contracts/agent.tool.schema.json vorhanden

# Push für einzelnes Repo
fleet-push repo="":
    @python3 scripts/fleet/push_template.py \
      --repo "{{repo}}" \
      --paths "templates/agent-kit" "contracts" \
      --message "feat: adopt agent-kit + contracts (wave 1)"

# Trockenlauf für einzelnes Repo
fleet-push-dry repo="":
    @python3 scripts/fleet/push_template.py \
      --repo "{{repo}}" \
      --paths "templates/agent-kit" "contracts" \
      --message "feat: adopt agent-kit + contracts (wave 1)" \
      --dry-run

# Push für alle Repos aus fleet/repos.yml
fleet-push-all:
    @python3 scripts/fleet/push_template.py \
      --paths "templates/agent-kit" "contracts" \
      --message "feat: adopt agent-kit + contracts (wave 1)"

# Local CI
validate: yq_ensure lint
    scripts/ci/validate-local.sh
    @if [ -d tests ] && [ -f pyproject.toml ] && grep -q "pytest" pyproject.toml; then echo "Running python tests..."; uv run pytest tests/; fi
    @printf "Running actionlint...\n"
    @scripts/tools/actionlint-pin.sh ensure
    @actionlint -color || (echo "::error::actionlint failed" && exit 1)
    @if [ -d contracts ]; then echo "contracts folder detected – run 'just contracts-validate' for schema checks"; fi

ci:
    just validate

contracts-validate:
    @scripts/validate-contracts.sh

e2e-dry:
    set -a; [ -f scripts/e2e/.env ] && . scripts/e2e/.env || true; set +a
    DRY_RUN=1 bash scripts/e2e/run_aussen_to_heimlern.sh

e2e:
    set -a; [ -f scripts/e2e/.env ] && . scripts/e2e/.env || true; set +a
    DRY_RUN=0 bash scripts/e2e/run_aussen_to_heimlern.sh
    bash scripts/e2e/report.sh

e2e-report:
    bash scripts/e2e/report.sh

# --- Interne Rezepte ----------------------------------------------------------
_wgx *args:
    @scripts/wgx {{args}}

_yq *args:
    @scripts/tools/yq-pin.sh {{args}}
# default: lint

# Lokaler Helper: Schnelltests & Linter – sicher mit Null-Trennung und Quoting
lint:
    @set -euo pipefail; \
    files=(); \
    while IFS= read -r -d '' file; do \
      files+=("$file"); \
    done < <(git ls-files -z -- '*.sh' '*.bash' 'scripts/wgx' 'wgx/wgx' ':!:completions/*' || true); \
    if [ "${#files[@]}" -eq 0 ]; then echo "keine Shell-Dateien"; exit 0; fi; \
    printf '%s\0' "${files[@]}" | xargs -0 bash -n; \
    scripts/tools/shfmt-pin.sh ensure; \
    scripts/tools/shellcheck-pin.sh ensure; \
    shfmt -d -i 2 -ci -sr -- "${files[@]}"; \
    shellcheck -S style -- "${files[@]}";
