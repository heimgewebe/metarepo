# Architektur

## Kernkomponenten (7 Schichten) — Stand v0.2

1. **Physisch (WGX/OS/systemd)** – Orchestrierung & Ausführung (wgx, just, Runner)
2. **Semantisch (semantAH)** – Embeddings, Graph, Relationen
3. **Operativ (hausKI)** – Planung, Simulation, Ausführung
4. **Reflexiv (sichter)** – Diagnose, Review, Selbstkorrektur
5. **Memorativ (leitstand)** – Episoden, Metriken, Audit-Persistenz
6. **Politisch-Adaptiv (heimlern)** – Policies, Bandits, Feedback/Score
7. **Dialogisch-Semantisch (mitschreiber, hausKI-audio)** – Intent, Kontext, Audio-Events

> **Nicht-Fleet:** `vault-gewebe` (privat) und `weltgewebe` (öffentlich, unabhängig) gehören nicht zur Fleet; sie werden nur referenziert.

Diese Seite fasst die wichtigsten Architektur-Perspektiven zusammen und verlinkt auf die
bestehenden Diagramme sowie Detaildokumente.

## Komponenten & Verantwortlichkeiten

- **aussensensor** – sammelt externe Signale, normalisiert sie in JSONL-Events und validiert gegen
  `contracts/aussen.event.schema.json`.
- **leitstand** – bietet das Ingest-API, persistiert Events und stellt Panels für Operator:innen.
- **heimlern** – verwaltet Policies, Entscheidungen (`policy.decision`), Snapshots und Feedback.
- **hausKI** – zentraler Orchestrator, koordiniert Entscheidungs- und Review-Schritte.
- **wgx** – Flottenmotor für Sync, Doctor, Smoke & Automatisierung.
- **semantAH** – erzeugt Insights & Graph-Artefakte für Berichte.
- **hauski-audio** – liefert Audio-/Telemetrie-Events.

Ausführliche Rollenbeschreibungen findest du in der [Systemübersicht](./system-overview.md) und in der
[Repo-Matrix](./repo-matrix.md).

## Datenflüsse

Der Kernpfad für Entscheidungsdaten lautet:

```
aussensensor → leitstand → heimlern → hausKI → leitstand
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
