# Automatisierung & CI

Diese Seite beschreibt die wichtigsten Automatisierungswerkzeuge, wiederverwendbaren Workflows und
Konventionen im Metarepo.

## Justfile-Targets

Die `Justfile` im Metarepo bündelt Fleet-Operationen. Häufig genutzte Targets:

| Target | Zweck |
| --- | --- |
| `just list` | zeigt alle bekannten Repos aus `repos.yml` |
| `just up` | spiegelt Templates (`templates/**`) in alle Repos |
| `just smoke` | Read-only Health-Checks über die gesamte Fleet |
| `just wgx:validate` | validiert `.wgx/profile.yml` Templates via `wgx` |
| `just validate` | führt lokale Validatoren aus (z. B. `yq`, JSON-Schemas) |
| `just e2e` / `just e2e-dry` | End-to-End-Läufe bzw. Dry-Run für `aussensensor → chronik → heimlern` |
| `just log-sync` | erzeugt einen neuen Bericht in [`reports/sync-logs/`](../reports/sync-logs) |

Weitere Ziele (z. B. `just fleet ...`) sind in der `Justfile` kommentiert beschrieben.

## WGX-Kommandos

`scripts/wgx` kapselt Flottenoperationen und ruft unter der Haube `wgx` auf. Nützliche Beispiele:

- `./scripts/wgx plan` – zeigt, welche Dateien in den Sub-Repos aktualisiert würden (Dry-Run).
- `./scripts/wgx run --repo <name> --cmd "just smoke"` – führt ein Kommando remote im Ziel-Repo aus.
- `./scripts/wgx doctor --repo <name>` bzw. `--all` – erstellt Drift-Berichte und legt sie unter
  [`reports/`](../reports) ab.

Weitere Hintergründe liefert [docs/fleet/wgx-konzept.md](../fleet/wgx-konzept.md).

## GitHub Workflows

Wesentliche wiederverwendbare Workflows liegen unter `.github/workflows/` und werden über Tags
(z. B. `contracts-v1`) versioniert:

- `reusable-validate-jsonl.yml` – JSONL-Validierung gegen ein Schema (`ajv`).
- `wgx-metrics.yml` – Validierung & optionaler Upload von Metrics-Snapshots.
- `org-assets.yml` – baut [Org-Index](../archive/org-index.md) und [Org-Graph](../archive/org-graph.mmd) und prüft Drift.

Sub-Repos binden diese Workflows via `uses: heimgewebe/metarepo/.github/workflows/...@<tag>` ein.
Details zu Parametern & Rollout-Prozessen stehen in [docs/policies/ci-reusables.md](./ci-reusables.md).

## Automatisierungs-Governance

- Änderungen an Templates und Workflows erfolgen über Pull-Requests mit Drift-Report.
- Tags (`contracts-vN`) frieren Schema- und Workflow-Versionen ein; Consumers pinnen auf den Tag.
- Reports unter [`reports/`](../reports) dokumentieren Doctor-/Smoke-Läufe und Sync-Aktionen.

## Weiterführende Links

- [Fleet-Operations](../fleet/fleet.md)
- [Templates](../templates.md)
- [Contract-Versionierung](../contracts/contract-versioning.md)
