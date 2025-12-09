# IDEal Blueprint: Das Heimgewebe-Modell

> Ein modulares, event-getriebenes System für persönliche Automatisierung und Wissensmanagement.

## Schichtenmodell (0-6)

- 0 Exekutiv · wgx (Aktion · Metriken)
- 1 Konnektiv · aussensensor (Außenwelt) · weltgewebe (Commons)
- 2 Prozedural · hausKI (Playbooks · Jobs · State)
- 3 Regulativ · heimlern (Policies · Rewards · Lernen)
- 4 Memorativ · chronik (Episoden · Metriken · Audit)
- 5 Semantisch · semantAH (Graph · Insights · Embedding)
- 6 Interaktiv · sichter (Review · Feedback · Prompt)

## Kern-Loop (vereinfacht)

**mitschreiber → semantAH → hausKI → heimlern → sichter → chronik → semantAH**

## Rollen im Detail

| Komponente | Rolle | Kernartefakte | Beispiel-Contract |
| --- | --- | --- | --- |
| wgx | Motorik | Shell-Skripte | `dev.tooling.schema.json` |
| hausKI | Orchestrator | `hauski.db` (SQLite), `events.jsonl` | `agent.workflow.schema.json` |
| heimlern | Policy Engine | Policy-Snapshots | `policy.decision.schema.json` |
| chronik | Persistenz · Panels | JSONL-Logs · Dashboards | aussen.event.schema.json |
| semantAH | Wissens-Graph | `.gewebe/index/*`, `insights/*.json` | `knowledge.graph.schema.json` |
| sichter | Review-UI | Review-Notizen, Feedback-Events | `review.feedback.schema.json` |
| mitschreiber | Kontext-Sensor | `os.context.intent.jsonl` | `os.context.intent.schema.json` |

## Roadmap-Phasen (Ziele)

1) **Contracts & Tooling (wgx)**
   - `just smoke` in jedem Repo
   - `wgx doctor` läuft
   - `wgx metrics snapshot` erzeugt valides JSON
2) **Core-Loop (hausKI → sichter → chronik)**
   - `sichter`-UI zeigt `hausKI`-Jobs
   - Reviews erzeugen `feedback`-Events
   - Bus-Demo (wgx→hausKI→sichter→chronik)
3. **Wissens-Integration (semantAH)**
   - `wgx knowledge extract` aus `vault-gewebe`
   - `semantAH` baut Index/Graph
   - `hausKI` kann `semantAH`-Fragen stellen
4) **Lern-Integration (heimlern)**
   - `heimlern` kann `hausKI`-Entscheidungen beeinflussen
   - `feedback`-Loop (sichter → heimlern) funktioniert
5) **Außenwelt (aussensensor)**
   - `aussensensor` liest externe Feeds
   - `chronik` zeigt Außen-Events
   - `heimlern` kann auf Außen-Events reagieren
