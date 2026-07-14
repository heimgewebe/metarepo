# Metarepo

> Versionierte Quelle für Fleet-Mitgliedschaft, gemeinsame Contracts, Templates und wiederverwendbare CI-Workflows.

[![CI Status](https://github.com/heimgewebe/metarepo/actions/workflows/ci.yml/badge.svg)](https://github.com/heimgewebe/metarepo/actions/workflows/ci.yml)

## Rolle und Wahrheitsgrenzen

Der normative Rollenvertrag liegt in
[`system/metarepo-role.v1.json`](system/metarepo-role.v1.json).

Metarepo besitzt ausschließlich folgende Wahrheitsbereiche:

- **Fleet-Mitgliedschaft** in [`fleet/repos.yml`](fleet/repos.yml)
- **gemeinsame Contracts** unter [`contracts/`](contracts/)
- **kuratierte Templates** unter [`templates/`](templates/)
- **wiederverwendbare CI-Workflows** unter [`.github/workflows/`](.github/workflows/)

Metarepo ist **keine Control Plane** und keine Quelle der gesamten
Systemarchitektur. Die Zuständigkeiten sind getrennt:

| Information | Zuständige Quelle |
| --- | --- |
| Systemzwecke, Beziehungen und Einstiegspunkte | `systemkatalog` |
| Aufgaben, Queue, Verifikation und Abschluss | `bureau` |
| Rechnerzugriff, Leases, Audit und operative Ausführung | `grabowski` |
| Laufzeitgesundheit | jeweiliger Dienst und seine Beobachtungsfläche |
| zeitliche Ereignis- und Änderungsgeschichte | `chronik` |

Die Mitgliedschaft in der Metarepo-Fleet ist nicht gleichbedeutend mit der
Zugehörigkeit zum vollständigen Operator-Ökosystem.

## Aktive Lieferflächen

### Fleet

[`fleet/repos.yml`](fleet/repos.yml) ist die normative Quelle der gemeinsam
verwalteten Metarepo-Fleet. Die gerenderte Übersicht wird daraus erzeugt:
[`docs/_generated/fleet.md`](docs/_generated/fleet.md).

Das Top-Level-[`repos.yml`](repos.yml) wird noch von bestehendem Tooling
verwendet. Es ist eine **nicht normative Legacy-Fläche** und soll zu einer
reproduzierbaren Projektion von `fleet/repos.yml` werden.

### Contracts

Unter [`contracts/`](contracts/) liegen versionierte Daten- und
Workflowverträge. Änderungen benötigen:

1. einen nachweisbaren Producer- oder Consumerbedarf;
2. Kompatibilitätsbewertung und Versionsentscheidung;
3. grüne Contract- und Consumer-Tests;
4. einen dokumentierten Ablösepfad bei Breaking Changes.

### Templates und wiederverwendbare Workflows

- `templates/` enthält kuratierte, repoübergreifend bestimmte Vorlagen.
- `.github/workflows/reusable-*.yml` und weitere `workflow_call`-Workflows
  werden von mehreren Repositories eingebunden.
- Aktive Consumer müssen vor Umbenennung oder Entfernung organisationsweit
  inventarisiert werden.

## Legacy- und Kompatibilitätsflächen

Diese Flächen sind weiterhin vorhanden, aber nicht Teil der normativen
Metarepo-Rolle:

- `repos.yml` – aktives Legacy-Manifest; Ziel: generierte Fleet-Projektion
- `wgx/` – vendierter Altstand; kanonischer Eigentümer ist das Repository `wgx`
- `servers/local-mcp/` – lokale Legacy-Brücke; Nutzung und Ablösung werden geprüft
- `.github/workflows/heimgewebe-command-dispatch.yml` – aktive
  Kompatibilitätsfläche mit organisationsweiten Callern

Sie dürfen erst entfernt werden, wenn ihre tatsächlichen Consumer und ein
grüner Migrations-Readback belegt sind.

## Historische Architekturdokumente

Die vorhandenen Dokumente zum früheren „Heimgewebe-Organismus“, insbesondere
unter `docs/system/`, sind **keine aktuelle Architekturwahrheit**. Sie bleiben
bis zur gesonderten Historisierung als Legacy-Material auffindbar. Für die
gegenwärtige Systemtopologie ist der Systemkatalog zuständig.

## Schnellstart

```bash
# Abhängigkeiten installieren
just deps

# lokale Validierung einschließlich Tests und Workflow-Linting
just validate

# Contract-Prüfungen
just contracts-validate

# Fleet-Übersicht
just list
```

## Typische Änderungen

### Contract ändern

1. Producer und Consumer bestimmen.
2. Schemaänderung und Kompatibilität prüfen.
3. Fixtures und Consumer-Tests aktualisieren.
4. Versionierung oder Migrationsfenster festlegen.

### Template ändern

1. Ziel- und Consumer-Repositories bestimmen.
2. lokale Abweichung nicht blind überschreiben.
3. Verbesserung kuratieren und im Metarepo testen.
4. Rollout über PRs mit Drift- und Consumerbeleg durchführen.

Beispiele für bestehendes Tooling:

```bash
./scripts/sync-templates.sh --pull-from <repo> --pattern "<glob>"
./scripts/sync-templates.sh --push-to <repo> --pattern "<glob>"
./scripts/wgx-doctor --repo <repo> --patterns "<glob1>,<glob2>"
```

## Dokumentation

- [Rollenvertrag](system/metarepo-role.v1.json)
- [Agentenleitfaden](AGENTS.md)
- [Contracts](docs/contracts/contracts-index.md)
- [Fleet-Management](docs/fleet/fleet.md)
- [Reusable CI](docs/policies/ci-reusables.md)
- [ADRs](docs/adrs/README.md)
- [Runbooks](docs/runbooks/runbooks.md)
- [Vollständiger Dokumentationsindex](docs/README.md)

## Projektstruktur

```text
metarepo/
├── system/              # Maschinenlesbare Rollen- und Wahrheitsverträge
├── fleet/               # Normative Fleet-Mitgliedschaft
├── contracts/           # Gemeinsame versionierte Contracts
├── templates/           # Kuratierte Shared Templates
├── .github/workflows/   # Reusable Workflows und Repo-CI
├── scripts/             # Sync-, Prüf- und Migrationswerkzeuge
├── docs/                # Metarepo-Dokumentation und Legacy-Material
├── reports/             # Nicht normative Befunde und Drift-Reports
├── repos.yml            # Legacy-Manifest; nicht normativ
└── Justfile
```

## Beitragen

Änderungen laufen über Pull Requests. Vor einem Merge müssen Diff,
Validierung, Consumer-Auswirkung und Wahrheitsgrenzen geprüft sein. Weitere
Details stehen in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Lizenz

Dieses Projekt steht unter der [CC0 1.0 Universal](LICENSE) Public Domain
Dedication. Die mitgelieferte actionlint-Dokumentation stammt vom
actionlint-Projekt und steht unter der MIT-Lizenz; siehe `LICENSE.txt`.
