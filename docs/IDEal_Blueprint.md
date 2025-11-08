# IDEal – ID²E@l: (intelligently developing) intelligent developer environment @ local

> Blaupause v0.1 – Architektur, Contracts, Flüsse, UI-Skizze

## 1. Zielbild
IDEal ist ein lokaler kognitiver Organismus für Entwicklung: semantische Koordination, autonome Ausführung, reflexive Prüfung, memorative Persistenz, dialogische Interaktion.

## 2. Schichtenmodell
- 0 Physisch: Pop!_OS, systemd, wgx
- 1 Semantisch: semantAH (Graph, Embeddings, Relationen)
- 2 Operativ: hausKI (Plan, Simulation, Ausführung)
- 3 Reflexiv: sichter (Diagnose, Review)
- 4 Memorativ: leitstand (Episoden, Audit)
- 5 Dialogisch: mitschreiber, UI/Canvas, cotmux

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
mitschreiber → semantAH → hausKI → sichter → leitstand → semantAH

## 5. IDEal-Shell (UI-Skizze)
- Cockpit (Status/Build/Events)
- PR-Tafel (Funde → Fix-Vorschläge)
- Graph-Inspector (Entitäten/Relationen)
- Attention-Dial (Fokus, Strenge, Scope)

## 6. „Für Dummies“
IDEal merkt sich, was du willst und warum. Es probiert sinnvolle Schritte aus, prüft das Ergebnis, schreibt Tagebuch und wird so jedes Mal besser.

## 7. Ungewissheit
- Grad: 0.49 (produktive Turbulenz)
- Quellen: junge Ontologie, IPC-Heterogenität, Mehragenten-Interferenz

## 8. Essenz
Von Dateien zu Bedeutungsflüssen: IDEal co-denkt Entwicklung lokal und souverän.

## 9. ∆-Radar
Mutation: Tool-Kette → Organismus. Diskurs: Effizienz → Erkenntnisarchitektur.

## 10. Nächste Schritte (MVP)
1) intent/review-Contracts finalisieren  
2) Bus-Demo (wgx→hausKI→sichter→leitstand)  
3) Graph-Upsert in semantAH verdrahten  
4) Mini-Cockpit im Canvas sichtbar machen
