# AGENTS.md — Metarepo

## Kanonischer Einstieg

Lies vor jeder Änderung:

1. [`system/metarepo-role.v1.json`](system/metarepo-role.v1.json)
2. [`.ai-context.yml`](.ai-context.yml)
3. den Live-Zustand von Branch, Worktrees, Leases, PRs und CI

Der Rollenvertrag ist normativ. README und dieser Leitfaden erklären ihn nur.

## Aufgabe des Repositories

Metarepo verwaltet vier gemeinsame Lieferbereiche:

- Fleet-Mitgliedschaft in `fleet/repos.yml`
- versionierte Contracts unter `contracts/`
- kuratierte Templates unter `templates/`
- wiederverwendbare CI-Workflows unter `.github/workflows/`

Metarepo ist keine Control Plane und kein vollständiger Systemkatalog.

## Getrennte Wahrheitsquellen

- **Systemkatalog:** Systemzwecke, Beziehungen, Zuständigkeitsgrenzen und Einstiegspunkte
- **Bureau:** Aufgaben, Queue, Verifikation und Abschluss
- **Grabowski:** operative Ausführung, Rechnerzugriff, Leases, Audit und Recovery
- **Chronik:** zeitliche Ereignis- und Änderungsgeschichte
- **jeweiliger Dienst:** eigene Laufzeitgesundheit

Diese Informationen nicht im Metarepo nachbauen oder aus Legacy-Dokumenten ableiten.

## Änderungsregeln

### Fleet

- `fleet/repos.yml` ist normativ.
- `repos.yml` ist eine nicht normative Legacy-Fläche.
- Fleet-Mitgliedschaft bedeutet nicht automatisch Zugehörigkeit zum gesamten Operator-Ökosystem.
- Repositories nur nach expliziten Aufnahmekriterien ergänzen oder entfernen.

### Contracts

Vor jeder Contract-Änderung:

1. Producer und Consumer live bestimmen.
2. Kompatibilität und Versionierung bewerten.
3. Fixtures sowie Producer- und Consumer-Tests ausführen.
4. Breaking Changes mit Migrations- und Entfernungskriterium versehen.

### Templates und reusable Workflows

- Aktive organisationsweite Consumer vor Änderung oder Entfernung suchen.
- Lokale Abweichungen nicht blind überschreiben.
- Verbesserungen aus Consumer-Repositories erst prüfen und kuratieren.
- Rollouts über getrennte PRs mit Drift- und Consumerbelegen durchführen.
- Externe Actions pinnen; bestehende Pinning-Policy beachten.

## Legacy- und Kompatibilitätsflächen

Folgende Pfade sind nicht Teil der normativen Rolle:

- `repos.yml`
- `wgx/`
- `servers/local-mcp/`

Der Workflow `.github/workflows/heimgewebe-command-dispatch.yml` ist weiterhin eine aktive Kompatibilitätsfläche. Keine dieser Flächen ohne vollständige Consumerinventur und grünen Migrations-Readback entfernen.

Die früheren Organismus- und Zielbilddokumente sind keine aktuelle Architekturwahrheit. Ihre Historisierung erfolgt gesondert.

## Sicherheits- und Arbeitsmodus

- Fremde Dirty-States, Worktrees, Branches, Prozesse und Leases nie resetten oder übernehmen.
- Änderungen in einem isolierten, sauberen Worktree ausführen.
- Vor nichttrivialem Merge vollständigen Diff bereitstellen und an Head sowie Diff-SHA-256 binden.
- Kein Shared Asset ohne belegte Consumer-Auswirkung mergen.
- Keine Secrets in Templates, Fixtures, Reports oder Workflow-Ausgaben schreiben.

## Prüfungen

```bash
just validate
just contracts-validate
python3 -m pytest tests/test_metarepo_role_contract.py
```

Für Template- und Fleet-Arbeit zusätzlich die betroffenen Drift-, WGX- und Consumer-Checks ausführen.

## Bestehendes Tooling

```bash
./scripts/sync-templates.sh --pull-from <repo> --pattern "<glob>"
./scripts/sync-templates.sh --push-to <repo> --pattern "<glob>"
./scripts/wgx-doctor --repo <repo> --patterns "<glob1>,<glob2>"
```

Diese Werkzeuge begründen keine Wahrheit außerhalb der im Rollenvertrag genannten Bereiche.
