# Contracts – Heimgewebe

> **Wahrheit:** `metarepo/contracts/*.schema.json` · **Policy:** [Contracts-First](./leitlinien.md#contracts-first)

Hier ist die Übersicht der zentralen Datenverträge (Schemas), die die Kommunikation zwischen den Heimgewebe-Komponenten regeln.

## Schema-Übersicht

| Schema | Kurzbeschreibung | Producer | Consumer |
| --- | --- | --- | --- |
| `contracts/dev.tooling.schema.json` | Werkzeug-Metadaten | `wgx`, IDE | `wgx doctor` |
| `contracts/agent.workflow.schema.json` | Agenten-Ablaufdefinition | `wgx agent` | `wgx agent run/trace` |
| `contracts/knowledge.graph.schema.json` | Wissensgraph-Elemente | `wgx knowledge extract` | `semantAH` |
| `contracts/insights.schema.json` | `semantAH` exportiert `vault/.gewebe/insights/today.json` | `chronik` zeigt Tageswissen, `hausKI` nutzt Fragen für Lern-Jobs |
| `contracts/audio.events.schema.json` | `hausKI-audio` Event-Stream | `chronik` Panels „Musik/PC“, `hausKI` zum Kontextlernen |
| `contracts/aussen.event.schema.json` | `aussensensor`, `weltgewebe` | `chronik` Panel „Außen“, Downstream Exports |
| `contracts/policy.decision.schema.json` | `heimlern` Policies | `hausKI` erklärt Entscheidungen („Warum“), `leitstand` (UI) zeigt Begründungen |
| `contracts/os.context.intent.schema.json` | `mitschreiber` | `semantAH` (Graph / Kontextaufbau), `hausKI` (Plan/Execute), `chronik` (Audit) |
| `contracts/events/intent.schema.json` *(Alias: intent_event)* | `mitschreiber` Intent-Sensorik | `hausKI` Planung, `chronik` Audit |
| `contracts/insights.schema.json` | `semantAH` | `hausKI`, `chronik` |
| `contracts/metrics.snapshot.schema.json` | `wgx` | `hausKI`, `chronik` |
| `contracts/knowledge.graph.schema.json` | `wgx knowledge extract`, Parser in `scripts/knowledge/*` | `semantAH` Ingest (Graph), `leitstand` Panel „Wissen“ |

## Versionierung & Rollout (Policy)

## Rollout-Checkliste

1.  **Strict SemVer** für alle Änderungen an Schemas.
2.  **Contracts-First:** Code-Änderungen, die neue Felder oder Strukturen nutzen, erfordern **zuerst** die Schema-Anpassung im `metarepo`.
3.  **Tags & Branches:** Reusable Workflows in der Fleet nutzen einen `contracts-vX` Tag, um gegen stabile Schema-Versionen zu validieren.
4.  **Rollout-Reihenfolge:** Producer (`wgx`, `semantAH`) zuerst mergen, danach Consumer (`hausKI`, `chronik`) und Policies (`heimlern`).

## CI/CD-Integration

-   **Reusable Workflow:** `reusable-validate-contracts.yml` prüft bei jedem Push in einem Fleet-Repo, ob die erzeugten JSON/JSONL-Dateien gegen die aktuellsten Schemas im `metarepo/main` validieren.
-   **Locking:**
    -   **Repos**: `repos.yml` definiert, welche Repos zur Fleet gehören und somit validiert werden.
    -   **Schemas**: `contracts/*.schema.json` eingefroren für Producer (`semantAH`, `wgx`, `hausKI-audio`, `aussensensor`) und Consumer (`hausKI`, `chronik`, `heimlern`).

---

## Siehe auch

- [Contract Versioning](./contract-versioning.md) – Rollout-Prozess für Schema-Änderungen
- [Contracts Overview](./contracts/index.md) – Contract-Index mit Details
- [ADR-0001: Contracts v1 & JSONL append-only](./adrs/0001-contracts-v1-jsonl.md) – Architekturentscheidung
- [Knowledge Contracts](./knowledge-contracts.md) – Spezielle Wissensverträge
- [Architecture](./architecture.md) – Systemarchitektur

[Zurück zur Übersicht](./README.md)

## Tool-Schemas

- `contracts/agent.tool.schema.json`: Canonical Fleet-Contract für Tool-Definitionen (wgx, Fleet-Push).
- `contracts/dev.tooling.schema.json`: Internes Metadaten-Schema für Metarepo-Tools (wgx doctor).
