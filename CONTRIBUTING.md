# Contributing to metarepo

Willkommen! Dieses Repo ist der Kanon für alle heimgewebe-Flotten. Damit Änderungen reibungslos in alle Sub-Repos fließen, befolge bitte den folgenden Ablauf.

## Setup & Grundprinzipien
- **Lizenz:** Beiträge stehen unter MIT (`SPDX-License-Identifier: MIT`).
- **Abhängigkeiten:**
  1. `uv sync --frozen` oder `just deps` installieren Tooling & Pins.
  2. Stelle sicher, dass `just` verfügbar ist; alle Standardkommandos laufen darüber.
- **Arbeitszweig:** Entwickle in einem Feature-Branch (`feat/...`, `chore/...`). Nutze aussagekräftige Commits (z. B. `feat(docs): add getting started guide`).

## Patch-Flow
1. **Synchronisation verstehen:**
   - `just list` → Welche Repos werden aktuell bedient?
   - `./scripts/wgx plan` → Vorschau, welche Dateien wohin gehen (`PLAN_LIMIT=0` zeigt alle).
2. **Änderungen vorbereiten:**
   - Templates spiegeln: `./scripts/sync-templates.sh --push-to <repo> --pattern "templates/**"` (oder `--pull-from` für Pull-Lernen).
   - Drift prüfen: `./scripts/wgx-doctor --repo <repo>` (Reports landen in `reports/`).
3. **Validieren:**
   - `just validate` – führt lokale Checks aus (`yq`-Validierung, Linting, etc.).
   - `just wgx_validate` – WGX-spezifische Konsistenzprüfungen.
   - Optional: `just test` – führt verfügbare Test-Suites aus.
   - Optional: `just smoke` – schneller Integrationslauf.
   - Optional: `just linkcheck` (benötigt Docker) für Docs-Links.
4. **Dokumentieren:**
   - Fleet- oder Sync-Run dokumentieren: `just log-sync` erzeugt Vorlage unter `reports/sync-logs/`.
   - Aktualisiere relevante Docs unter `docs/` oder `templates/` (bitte AGENTS.md-Hinweise beachten).

## Pull Requests
- **Template nutzen:** Fülle `.github/pull_request_template.md` vollständig aus (ADR-Abschnitt nur, wenn relevant).
- **Tests anhängen:** Liste im PR mindestens `just validate` (und weitere relevante Kommandos) samt Ergebnis.
- **Review-Kontext:** Notiere Besonderheiten im Abschnitt „Review-Notizen“ (z. B. welche Sub-Repos ein Follow-up benötigen).
- **Reconciliation:** Wenn du Templates aus Sub-Repos übernimmst, referenziere die Quelle (`<repo>@<sha>`).

## Contracts pflegen
Wenn du Änderungen an Daten-Contracts vornimmst:

- **Zentrale metarepo-Contracts:** Wenn neue Dateien unter `contracts/*.schema.json` angelegt, umbenannt oder gelöscht werden, aktualisiere `docs/contracts-index.md` in derselben PR.
- **Repo-spezifische Contracts:** Falls ein Contract in einem anderen Repo systemweit relevant ist (Events, Policy, Weltgewebe-Domain etc.), ergänze einen Eintrag in `docs/contracts-index.md`.
- **CI-Check:** Ein automatischer Guard prüft, dass alle zentralen `contracts/*.schema.json`-Dateien im Index referenziert sind.

## Nach dem Merge
- Führe bei Bedarf `./scripts/sync-templates.sh --push-to <repo>` aus, um die aktualisierten Templates zu verteilen.
- Aktualisiere Downstream-Issues/Docs, falls deine Änderung Koordination benötigt.

Danke fürs Mitbauen – jede Verbesserung im metarepo spart Arbeit in allen Flotten-Repos!
