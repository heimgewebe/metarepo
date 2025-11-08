# IDEal – ID²E@l: (intelligently developing) intelligent developer environment @ local

> **Version:** v0.2 – Stand November 2025
> (aktualisiert mit `mitschreiber`, neuen Datenflüssen und Schichtdefinitionen)

## 1. Zielbild
IDEal ist ein lokaler kognitiver Organismus für Entwicklung:
semantische Koordination • autonome Ausführung • reflexive Prüfung • memorative Persistenz • dialogische Interaktion.

## 2. Schichtenmodell
- 0 Physisch · Pop!_OS · systemd · wgx
- 1 Semantisch · semantAH (Embeddings & Graph)
- 2 Operativ · hausKI (Plan · Simulation · Ausführung)
- 3 Reflexiv · sichter (Diagnose · Review · Selbstkorrektur)
- 4 Memorativ · leitstand (Episoden · Metriken · Audit)
- 5 Politisch-Adaptiv · heimlern (Policies · Lern-Feedback · Scores)
- 6 Dialogisch-Semantisch · mitschreiber (Intent · Kontext · Text- & State-Embeddings)

## 3. Heimgewebe-Bus (IPC)
- Transport: systemd-sockets/FIFO (lokal), Payload JSONL
- Topics (Auszug):
  - intent/declare
  - plan/execute
  - review/report
  - graph/upsert
  - state/metric
  - insight/emit
  - error/event

### 3.1 Contracts (Skizzen)
```json
// contracts-v1/events/intent.schema.json (Skizze)
{
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "type":"object",
  "required":["id","actor","goal","scope","ts"],
  "properties":{
    "id":{"type":"string"},
    "actor":{"type":"string"},
    "goal":{"type":"string"},
    "scope":{"type":"object"},
    "constraints":{"type":"object"},
    "ts":{"type":"string","format":"date-time"}
  }
}
```
```json
// contracts-v1/events/review.schema.json (Skizze)
{
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "type":"object",
  "required":["repo","sha","findings","ts"],
  "properties":{
    "repo":{"type":"string"},
    "sha":{"type":"string"},
    "findings":{"type":"array","items":{"type":"object"}},
    "fixes":{"type":"array","items":{"type":"object"}},
    "ts":{"type":"string","format":"date-time"}
  }
}
```

## 4. Semantischer Blutkreislauf
**mitschreiber → semantAH → hausKI → heimlern → sichter → leitstand → semantAH**

*Alle Komponenten kommunizieren über den Heimgewebe-Bus
(lokales JSONL-Eventsystem mit Topics `intent/*`, `graph/*`, `review/*`, `policy/*`, `state/*`, `insight/*`, `error/*`).*

## 5. IDEal-Shell (UI-Skizze)
- Cockpit (Status/Build/Events)
- PR-Tafel (Funde → Fix-Vorschläge)
- Graph-Inspector (Entitäten/Relationen)
- Attention-Dial (Fokus, Strenge, Scope)

## 5a. Repos & Zuständigkeiten (Core Fleet)

| Repo | Rolle | Hauptoutput | Contracts |
|:--|:--|:--|:--|
| metarepo | Control-Plane · Contracts · CI-Templates | Schemas · Docs | contracts/*.schema.json |
| wgx | System-Motorik · CLI · Automation | Metrics-Snapshots | metrics.snapshot.schema.json |
| hausKI | Orchestrator · Planer | Events · Decisions | event.line · policy.decision |
| heimlern | Policy-Lernen · Scorer | Entscheidungen („why“) | policy.decision.schema.json |
| semantAH | Wissensgraph · Embeddings | insights/*.json | insights.schema.json |
| leitstand | Persistenz · Panels | JSONL-Logs · Dashboards | aussen.event.schema.json |
| hausKI-audio | Audio-Events | – | audio.events.schema.json |
| aussensensor | Außenfeeds | feed.jsonl | aussen.event.schema.json |
| mitschreiber | Intent-Sensorik · OS-Kontext | os.context.* | os.context.text.embed.schema.json |

## 6. „Für Dummies“
IDEal merkt sich, was du willst und warum. Es probiert sinnvolle Schritte aus, prüft das Ergebnis, schreibt Tagebuch und wird so jedes Mal besser.

## 7. Ungewissheit
- Grad ≈ 0.49 · produktive Turbulenz

| Ursache | Art | Auswirkung |
|:--|:--|:--|
| Ontologie im Aufbau | epistemisch | Intent-Ambiguität |
| Mehragenten-Interaktion | systemisch | Synchronitäts-Konflikte |
| Heterogener IPC | technisch | Latenz · Race Conditions |
| Kontext-Überlappung | organisatorisch | Priorisierung / Backpressure nötig |

## 8. Essenz
Von Dateien zu Bedeutungsflüssen: IDEal co-denkt Entwicklung lokal und souverän.

## 9. ∆-Radar
Mutation: Tool-Kette → Organismus. Diskurs: Effizienz → Erkenntnisarchitektur.

## 10. Nächste Schritte (MVP)
1) intent/review-Contracts finalisieren  
2) Bus-Demo (wgx→hausKI→sichter→leitstand)  
3) Graph-Upsert in semantAH verdrahten  
4) Mini-Cockpit im Canvas sichtbar machen
