# Heimgewebe – Architektur (Schichten & Komponenten)

> Ergänzung zur Übersicht: konsistente Benennung aller Kern-Komponenten und klare Abgrenzung von Nicht-Fleet Repos.

## Schichtenmodell (0–6)
- **0 Physisch** · OS / systemd / wgx
- **1 Semantisch** · **semantAH** (Embeddings & Graph)
- **2 Operativ** · **hausKI** (Plan · Simulation · Ausführung)
- **3 Reflexiv** · **sichter** (Diagnose · Review · Selbstkorrektur)
- **4 Memorativ** · **leitstand** (Episoden · Metriken · Audit)
- **5 Politisch-Adaptiv** · **heimlern** (Policies · Lern-Feedback · Scores)
- **6 Dialogisch-Semantisch** · **mitschreiber** (Intent · Kontext · Text- & State-Embeddings)

## Fleet (Core-Repos)
- `metarepo` · Control-Plane, Contracts, Reusable Workflows
- `wgx` · System-Motorik & Automation
- `hausKI` · Orchestrator/Planner
- `heimlern` · Policy-/Bandit-Layer
- `semantAH` · Wissensgraph/Insights
- `leitstand` · Ingest & Panels
- `hausKI-audio` · Audio-Events
- `aussensensor` · Außenfeeds → kuratierte Events
- `mitschreiber` · Intent-/Kontext-Sensorik

## Nicht-Fleet (explizit)
- **vault-gewebe** (inkl. privat) – persönlicher Wissensspeicher
- **weltgewebe** – unabhängiges Projekt; kann Signale liefern, gehört aber **nicht** zur Fleet

Siehe auch: [`docs/overview.md`](./overview.md), [`docs/contracts.md`](./contracts.md).