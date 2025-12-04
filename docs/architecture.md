# Architektur

## Kernkomponenten (7 Schichten) — Stand v0.2

1. **Physisch (WGX/OS/systemd)** – Orchestrierung & Ausführung (wgx, just, Runner)
2. **Semantisch (semantAH)** – Embeddings, Graph, Relationen
3. **Operativ (hausKI)** – Planung, Simulation, Ausführung
4. **Reflexiv (sichter)** – Diagnose, Review, Selbstkorrektur
- **Memorativ (chronik)** – Event-Ingest, Persistenz, Audit-Trails
6. **Politisch-Adaptiv (heimlern)** – Policies, Bandits, Feedback/Score
- **Interaktiv/Dialogisch (leitstand, mitschreiber, hausKI-audio)** – UI, Intent, Kontext, Audio-Events

> **Nicht-Fleet:** `vault-gewebe` (privat) und `weltgewebe` (öffentlich, unabhängig) gehören nicht zur Fleet; sie werden nur referenziert.

Diese Seite fasst die wichtigsten Architektur-Perspektiven zusammen und verlinkt auf die
bestehenden Diagramme sowie Detaildokumente.

## Komponenten & Verantwortlichkeiten

- **aussensensor** – sammelt externe Signale, normalisiert sie in JSONL-Events und validiert gegen
  `contracts/aussen.event.schema.json`.
- **chronik** – bietet das Ingest-API (`POST /ingest/{domain}`), persistiert Events in JSONL,
  führt Audit-Trails und stellt Snapshots/Exports bereit.
- **heimlern** – verwaltet Policies, Entscheidungen (`policy.decision`), Snapshots und Feedback.
- **hausKI** – zentraler Orchestrator, koordiniert Entscheidungs- und Review-Schritte.
- **leitstand** – UI/Dashboard; zeigt Panels (PC, Musik, Heute, Außen), Digests und verbindet
  Daten aus chronik, semantAH und hausKI.
- **wgx** – Flottenmotor für Sync, Doctor, Smoke & Automatisierung.
- **semantAH** – erzeugt Insights & Graph-Artefakte für Berichte.
- **hausKI-audio** – liefert Audio-/Telemetrie-Events.

Ausführliche Rollenbeschreibungen findest du in der [Systemübersicht](./system-overview.md) und in der
[Repo-Matrix](./repo-matrix.md).

## Datenflüsse

Der Kernpfad für Entscheidungsdaten lautet:

```
aussensensor → chronik → heimlern → hausKI → leitstand
```

Weitere Flüsse (Metrics, Insights, Audio) sind im [Heimgewebe-Datenfluss](./heimgewebe-dataflow.mmd)
und unter [Events & Contracts](./contracts/index.md) aufgeführt.

## Diagramme

- Mermaid: [`docs/heimgewebe-architektur.mmd`](./heimgewebe-architektur.mmd)
- Mermaid: [`docs/heimgewebe-dataflow.mmd`](./heimgewebe-dataflow.mmd)
- Canvas: [`docs/canvas/heimgewebe-architektur.canvas`](./canvas/heimgewebe-architektur.canvas)
- Canvas: [`docs/canvas/heimgewebe-dataflow.canvas`](./canvas/heimgewebe-dataflow.canvas)

## Verträge & Versionierung

- Überblick in [Events & Contracts](./contracts/index.md)
- Details & Rollout-Prozess in [Contract-Versionierung](./contract-versioning.md)
- JSON-Schemas unter [`contracts/`](../contracts) (Tag `contracts-vN`)

## Weiterführende Architekturthemen

- [Heimgewebe – Überblick](./heimgewebe-gesamt.md) – narrative Gesamtsicht
- [Vision](./vision.md) – Leitlinien & Zukunftsbild
- [Kernkonzepte](./konzept-kern.md) – Governance, Sync, Drift
- [System Overview](./system-overview.md) – Kurzübersicht der Komponenten
- [ADRs](./adrs/README.md) – Architekturentscheidungen
- [Repo Matrix](./repo-matrix.md) – Repository-Rollen im Detail
