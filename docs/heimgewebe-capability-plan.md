# Heimgewebe – Capability-Plan (Observatorium, Intent, Metabrain)

## 1. Ausgangslage

- Heimgewebe-Zielbild ist definiert (`docs/heimgewebe-zielbild.md`).
- Organe und Achsen sind beschrieben (Events, Semantik, Commands, WGX, OS-Kontext).
- Es fehlen zentrale Capabilities:
  - Semantisches Observatorium
  - Intent-Resolver / Intelli-Orchestrator
  - Projekt-Metabrain / Szenarien
  - Selbstverbesserungs-Loop (Organismus lernt über sich)
  - Forschungs-Kopilot (als Querschnitt)

## 2. Leitprinzipien

1. Contracts first – neue Fähigkeiten beginnen mit Schemas im Metarepo.
2. Keine neuen Repos in Phase 1 – wir bauen Caps in bestehende Organe.
3. Jede Capability muss mindestens:
   - ein Contract-Schema,
   - einen Producer (Job/Service),
   - einen Konsumenten (Leitstand-View oder hausKI-Logik) haben.
4. Events statt versteckter Logik – alle Capabilities erzeugen Events/Snapshots.

## 3. Capability C1 – Semantisches Observatorium

### 3.1 Ziel

- Heimgewebe erzeugt explizite Themenräume und Forschungsbrennpunkte.
- Operator sieht: "Worüber denken wir gerade intensiv nach?"

### 3.2 Änderungen

- Neues Schema: `contracts/knowledge.observatory.schema.json` (Metarepo).
- Neuer Job in `semantAH`:
  - Input: Vault, chronik, OS-Kontext.
  - Output: Observatory-Snapshot nach Schema.
- Neue View in `leitstand`:
  - "Themenräume heute" – Liste mit Kurzbeschreibung.

### 3.3 Akzeptanzkriterien (MVP)

- Mindestens 3 Topics werden erzeugt.
- Jede Topic hat:
  - Titel,
  - Anzahl verknüpfter Quellen,
  - eine vorgeschlagene Frage.

## 4. Capability C2 – Intent-Resolver (Intelli-Orchestrator light)

### 4.1 Ziel

- Heimgewebe erkennt den groben Arbeitskontext (Coding, Schreiben, Research ...).
- Intents sind als Events sichtbar und maschinenlesbar.

### 4.2 Änderungen

- Schärfung von `contracts/os.context.intent.schema.json`.
- Erweiterung `mitschreiber`:
  - erzeugt strukturierte OS-Kontext-Ereignisse.
- Neuer Resolver in `hausKI`:
  - mappt OS-Kontext → Intent-Events.
- Leitstand-Widget "Aktueller Intent".

### 4.3 Akzeptanzkriterien (MVP)

- System erzeugt Intent-Events mit Confidence.
- Intent-Switches können im Leitstand über Zeit verfolgt werden.

## 5. Capability C3 – Projekt-Metabrain / Szenarien

(... wie oben beschrieben, kurz ausformulieren ...)

## 6. Capability C4 – Selbstverbesserungs-Loop

(... Beschreibung von policy.decision + policy.feedback Pipeline ...)

## 7. Roadmap-Phasen

- **Phase 0 – Doku & Contracts (2–3 Sessions)**
  - Alle neuen Schemas skizziert und im Metarepo abgelegt.
- **Phase 1 – C1 + C2 (MVP)**
  - Observatorium + Intent-Resolver in klein.
- **Phase 2 – C3 (Szenarien)**
  - Erste Szenariogenerierung über heimgeist.
- **Phase 3 – C4 (Selbst-Loop)**
  - Policy-Feedback mit heimlern.
- **Phase 4 – Forschungs-Kopilot**
  - Spezialisierter hausKI-„Research“-Modus auf Basis von C1–C3.

## 8. Risiken & Trade-offs

- Fragmentierung vermeiden – keine neuen Repos vor Phase 3.
- Komplexität der Semantik – Observatorium zunächst heuristisch, nicht „perfekt“.
- Selbstverbesserung darf Operator nicht entmündigen:
  - Policies bleiben menschlich überschreibbar.

## 9. Essenz

- Fehlende Idee: Heimgewebe hat noch keinen inneren Sinnkreislauf.
- Lösung: Vier Capabilities, die auf bestehende Organe aufsetzen.
- Dokumentation: Ein gemeinsamer Capability-Plan statt verstreuter Einzeldokus.
