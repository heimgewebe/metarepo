# Fleet-Operations im metarepo

Das **metarepo** ist die Flotten-Leitstelle für alle Repositories unter `heimgewebe`.
Es hält das Inventar (`repos.yml`), verteilt Templates/CI-Reusables und stößt WGX-Läufe an.
Die kanonische WGX-Dokumentation bleibt im [WGX-Repository](https://github.com/heimgewebe/wgx).

## Verantwortungsabgrenzung
- **metarepo**
  - Kuratiert Fleet-Scope und Standard-Templates (`templates/**`).
  - Pflegt wiederverwendbare Workflows und Runbooks.
  - Initiiert Fleet-Zyklen über `just` oder `scripts/wgx`.
- **WGX-Repo**
  - Enthält Master-Doku, Policies und Guard-Implementierung.
  - Liefert die ausführbare Engine; metarepo ruft sie nur auf.

## Fleet-Zyklus (sync → validate → smoke)
1. **sync** – `just up` oder `./scripts/wgx up`
   - Spiegelt die Templates/Runbooks in jedes Ziel-Repo.
   - Nutzt `templates/**` als Quelle der Wahrheit.
2. **validate** – `just wgx:validate` oder `./scripts/wgx validate`
   - Prüft `repos.yml` auf Schemafehler und verifiziert, dass Pflicht-Templates vorhanden sind.
   - Ergänzend `just validate` für lokale YAML-/Template-Checks (yq v4).
   - Optional ergänzen durch `./scripts/wgx-doctor` für Drift-Analysen.
3. **smoke** – `just smoke` oder `./scripts/wgx smoke`
   - Triggert die WGX-Smoke-Workflows in jedem Repo (`wgx-smoke.yml`).
   - Ergebnis dient als Fleet-Gesundheitsindikator.

> 💡 Detailwissen zu WGX-Kommandos, Guards oder Profilen wird **nicht** im metarepo verdoppelt.
> Link stattdessen direkt auf die Master-Doku im WGX-Repo.

## Betriebsnotizen
- `reports/` sammelt Ausgaben von Drift-/Doctor-Läufen.
- Fleet-Änderungen immer mit kurzem Incident-Log in PR-Beschreibung dokumentieren.
- Für Ad-hoc-Syncs einzelner Repos `scripts/sync-templates.sh --push-to <repo> --pattern "templates/**"` nutzen.

## Siehe auch

- [WGX Konzept](./wgx-konzept.md) – Fleet-Motor Konzept und Kommandos
- [Templates](./templates.md) – Template-Verteilung im Detail
- [Push to Fleet](./fleet/push-to-fleet.md) – Detaillierte Fleet-Deployment-Prozesse
- [Repo Matrix](./repo-matrix.md) – Repository-Rollen und Status
- [ADR-0002: Fleet-Rollout via reusable GitHub Actions](./adrs/0002-reusable-actions-rollout.md) – Entscheidungsgrundlage
