# metarepo · Docs-Index (Tower)
Diese Dokumente beschreiben **Fleet/Themen** des metarepo (Inventar, Verteilung, CI-Reusables, Drift).
Für **WGX (Engine)** siehe: https://github.com/heimgewebe/wgx

## Schnelleinstieg
- [Systemübersicht](./system-overview.md) – Repos, Rollen & Einstiegspunkte
- [Architektur](./architecture.md) – Komponenten, Datenflüsse & Diagramme
- [Use-Cases](./use-cases.md) – typische Abläufe Schritt für Schritt
- [Automatisierung & CI](./automation.md) – Just-Targets, Workflows, WGX
- [Umgebung & Secrets](./environment.md) – lokale Konfiguration & Token-Hinweise
- [Troubleshooting & FAQ](./troubleshooting.md) – häufige Fehler & Lösungen
- [Events & Contracts](./contracts/index.md) – Schemas & Versionierung
- [End-to-End-Läufe](./e2e.md) – Kette `aussensensor → leitstand → heimlern`

## Vertiefung & Referenzen
- [Kernkonzepte (Architektur, Sync, Drift)](./konzept-kern.md)
- [Fleet-Kurzüberblick (Rollen, Flüsse, Auth)](./overview.md)
- [Fleet-Operations](./fleet.md)
- [repos.yml – Inventar & Filter](./repos.yml.md)
- [Templates verteilen & driftfrei halten](./templates.md)
- [CI-Reusables](./ci-reusables.md)
- [Runbooks verteilen](./runbooks.md)
- [WGX-Doku-Stubs](./wgx-stub.md)
- [Leitlinien](./leitlinien.md)
- [Heimgewebe — Überblick (Ideales Gesamtsystem)](./heimgewebe-gesamt.md)
- [Vision & Architekturüberblick](./vision.md)
- [Contract-Versionierung](./contract-versioning.md)
- [Architecture Decision Records (ADRs)](./adr/README.md)

## Visuals & Diagramme
- [Architektur (Mermaid)](./heimgewebe-architektur.mmd)
- [Datenfluss (Mermaid)](./heimgewebe-dataflow.mmd)
- [Architektur (Canvas)](./canvas/heimgewebe-architektur.canvas)
- [Datenflüsse (Canvas)](./canvas/heimgewebe-dataflow.canvas)

## Diagramm-Rendering
- Lokal: `scripts/render-diagram.sh docs/IDEal_Blueprint.md --outdir docs/diagrams --format png`
- CI: Workflow **render-diagrams** (liefert Artefakt `diagrams-<run_id>`)
