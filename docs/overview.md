# Heimgewebe Fleet – Kurzüberblick

> **Kernabgrenzung:** Die Heimgewebe-**Fleet** besteht aus den *Core-Repos*. Zusätzlich existieren verwandte Repos, die parallel entwickelt werden oder persönliche Daten enthalten, aber **nicht** zur Fleet zählen.

## Rollen (Control vs. Ausführung)
- **metarepo** · Control-Plane, Verträge & Reusable Workflows (Tags wie `contracts-v1`)
- **wgx** · Motorik & PC-Wartung (führt Playbooks aus, liefert Metrics)
- **hausKI** · Orchestrator, Persistenzkern, Policy-Hub (`jobs`, Events, Decisions)
- **semantAH** · Wissensaufbereitung & Insights (`vault/.gewebe/insights/*`)
- **heimlern** · Policy-/Bandit-Layer (`decide`, `feedback`, `why`)
- **leitstand** · Panels & Digest (zeigt „Was/Warum/Resultat“)
- **hausKI-audio** · Audio/Telemetrie, Sessions & Routing
- **aussensensor** · Außenwelt-Signale → kuratierte Events

## Core-Repos (Fleet)
- **wgx**, **hausKI**, **hausKI-audio**, **metarepo**, **heimlern**, **aussensensor**, **leitstand**, **semantAH**

## Verwandte Repos (nicht Teil der Fleet)
- **vault-gewebe** *(inkl. privater Anteile)*: persönlicher Wissensspeicher des Autors; kein Fleet-Target.
- **weltgewebe**: unabhängiges Projekt (Außensphäre/Community/Karten). Wird parallel mitentwickelt; kann Events/Signale liefern, gehört aber **nicht** zur Fleet.

## Datenflüsse (produzierende→konsumierende Komponenten)
- `semantAH → hausKI/leitstand`: `insights/*.json`, Weekly Reports
- `wgx → hausKI/leitstand`: `metrics.snapshot.json`
- `hausKI-audio → hausKI/leitstand`: Session-/Latenz-Events
- `aussensensor → leitstand`: Außen-Event-Streams (`feed.jsonl`)
- `mitschreiber → semantAH` *(optional zusätzlich → leitstand)*: **Intents** (`os.context.intent.jsonl`)
- *(optional)* `weltgewebe → aussensensor/leitstand`: geteilte Außenposts/Projekte (außerhalb der Fleet).
- `heimlern ↔ hausKI`: `decide(ctx)` → `action, why`; `feedback(reward)`
- `hausKI → wgx/hausKI-audio`: Playbook-Aufträge & Steuerungsbefehle

## Authentisierung & Vertrauensanker
- **Lokal-first**: Primäre Interaktion auf Geräten, keine Fremd-Cloud
- **mTLS** zwischen Diensten (`hausKI`, `leitstand`, `aussensensor`)
- **Signierte Event-Ingests** (Replay-Schutz, Append-only Verträge)
- **Tags + Schemas**: Contracts (`contracts/*.schema.json`) & Workflow `.github/workflows/reusable-validate-jsonl.yml` werden über Tags gepflegt (z. B. `contracts-v1`)
  → Consumer pinnen auf den Tag

### Optionales Betriebsmodell: Single Point of Ingest
Statt `aussensensor` parallel an `leitstand` **und** `heimlern` senden zu lassen, kann `leitstand` als *einziger* Ingest-Punkt fungieren. Downstream-Dienste (z. B. `heimlern`) beziehen ihre Events dann **aus** `leitstand` (Event-Sourcing-Pattern). Vorteile: geringere Kopplung, klarere Verantwortlichkeit, zentralisiertes Auditing.

## Leitplanken für Releases
- Neue Contracts → Branch & Review im metarepo, Dokumentation unter [`docs/contracts/index.md`](./contracts/index.md)
- Reusable Workflow (`.github/workflows/reusable-validate-jsonl.yml`) in Sub-Repos via `uses: ...@contracts-v1`
- Obsidian-Canvas (`docs/canvas/*.canvas`) spiegeln Architektur & Flüsse, dienen als visuelle Referenz
- Übersichtliche Gesamtdarstellung: [`docs/heimgewebe-gesamt.md`](./heimgewebe-gesamt.md)

## Contracts ↔ Repos
| Contract | Producer | Consumer |
| --- | --- | --- |
| [`metrics.snapshot`](../contracts/metrics.snapshot.schema.json) | wgx | hausKI, leitstand |
| [`insights`](../contracts/insights.schema.json) | semantAH | hausKI, leitstand |
| [`audio.events`](../contracts/audio.events.schema.json) | hausKI-audio | hausKI, leitstand |
| [`aussen.event`](../contracts/aussen.event.schema.json) | aussensensor, weltgewebe | leitstand |
| [`event.line`](../contracts/event.line.schema.json) | weltgewebe | hausKI, leitstand |
| [`policy.decision`](../contracts/policy.decision.schema.json) | heimlern | hausKI |
| [`os.context.intent`](../contracts/os.context.intent.schema.json) | mitschreiber | semantAH, hausKI, leitstand |
