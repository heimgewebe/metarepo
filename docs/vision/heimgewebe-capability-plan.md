# Heimgewebe – Capability-Plan (Observatorium, Intent, Metabrain)

## 1. Ausgangslage

- Heimgewebe-Zielbild ist definiert (`docs/system/heimgewebe-zielbild.md`).
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

Heimgewebe soll dir 1× täglich sagen:
„Das sind gerade deine wichtigsten Themenräume, inklusive Quellen und einer Leitfrage.“

Der Operator sieht: "Worüber denken wir gerade intensiv nach?"

### 3.2 Umsetzung (Phase 1)

**In semantAH** (Neuer Job / Script):
- **Input:**
  - Vault-Schnipsel (z. B. markierte Ordner in `vault-gewebe`).
  - Ausgewählte Events aus `chronik` (`event.line`).
- **Output:**
  - Datei oder Event nach `knowledge.observatory.schema.json`.
  - Z. B. `observatory-YYYY-MM-DD.json` im Output-Verzeichnis oder als Event.
- **Heuristik (MVP):**
  - Topics via Tag- oder Ordnerstruktur im Vault.
  - Erwähnungshäufigkeit von Repos / Begriffen in Notizen.
  - Pro Topic: Titel, Liste der Quellen (Notizen, Events), eine „offene Frage“ (z. B. per einfacher LLM-Prompt-Logik).

**In leitstand** (Neue View):
- Neues Panel „Themenräume“.
- Liste der aktuellen Topics.
- Klick zeigt Quellen + Frage.

**In chronik** (Optional MVP+):
- Option, Observatorium-Snapshot als `event.line` abzulegen, damit man über Zeit sehen kann, wie sich Themen verschieben.

### 3.3 Akzeptanzkriterien (MVP)

- Mindestens 3 Topics werden erzeugt.
- Jede Topic hat:
  - Titel,
  - Anzahl verknüpfter Quellen,
  - eine vorgeschlagene Frage.

### 3.4 Für Dummies (Zusammenfassung)

SemantAH baut jeden Tag eine kleine „Landkarte“ deiner aktuellen Themen: „Woran arbeitest du eigentlich?“ Leitstand zeigt dir das als Liste an.

## 4. Capability C2 – Intent-Resolver (Intelli-Orchestrator light)

### 4.1 Ziel

Heimgewebe erkennt:
„Alexander ist gerade im Modus X (z. B. Coding an Repo Y, Schreiben, Research)“
und macht das als Event sichtbar und maschinenlesbar.

### 4.2 Umsetzung (Phase 1)

- **Schärfung** von `contracts/os.context.intent.schema.json`.

**In mitschreiber**:
- Sicherstellen, dass `os.context.state` Events zuverlässig entstehen:
  - Welche App/Fenster aktiv?
  - Welche Datei / welches Repo? (so weit möglich)

**In hausKI** (Neuer Resolver-Job):
- **Input:** Aktuelle/letzte `os.context.state` Events.
- **Logik (MVP):** Einfache Regeln:
  - VSCode + Git → „coding“
  - Obsidian → „writing“ oder „thinking“
  - Browser + GitHub → „repo-browsing“
- **Output:** `os.context.intent` Events nach dem Contract:
  - `intent_type`, `confidence`, `context_refs` (Repo, Datei, App).

**In leitstand** (Widget "Aktueller Intent"):
- Anzeige des aktuellen Intents + Verlauf (Timeline der letzten X Intents).

### 4.3 Akzeptanzkriterien (MVP)

- System erzeugt Intent-Events mit Confidence.
- Intent-Switches können im Leitstand über Zeit verfolgt werden.

### 4.4 Für Dummies (Zusammenfassung)

Mitschreiber beobachtet, was du am Rechner machst. HausKI übersetzt das in „Arbeitsmodus“-Events („Er schreibt“, „er codet“). Leitstand zeigt dir das wie eine Statusanzeige an.

## 5. Capability C3 – Projekt-Metabrain / Szenarien

### 5.1 Ziel

Für ausgewählte Themenräume / Projekte soll Heimgewebe 2–3 Szenarien vorschlagen:
- konservativ
- ambitioniert
- experimentell

Inklusive Annahmen und Risiken.

### 5.2 Umsetzung (Phase 2)

**In metarepo**:
- `contracts/project.scenario.schema.json` konkret machen:
  - `scenario_id`, `project_id` (oder `topic_id` aus Observatorium).
  - `label` (konservativ/ambitioniert/experimentell).
  - `description`.
  - `assumptions[]`.
  - `risks[]`.
  - `suggested_actions[]`.

**In heimgeist** (Job „Szenarien-Generator“):
- **Input:** Observatorium-Topics (C1), eventuell `os.context.intent` (C2).
- **Output:** Pro aktivem Topic 2–3 Szenarien nach `project.scenario`-Schema.
- Speicherung als `event.line` mit Typ `project.scenario`.

**In leitstand** (Erweiterung Themenraum-Panel):
- Zu jedem Topic Button „Szenarien anzeigen“.
- Liste der Szenarien mit Assumptions/Risks in kompakter Form.

### 5.3 Für Dummies (Zusammenfassung)

Heimgeist nimmt ein wichtiges Thema (z. B. „Heimgewebe-Doku aufräumen“) und schlägt dir drei Wege vor: einen vorsichtigen, einen mittleren, einen radikalen, jeweils mit „Was bräuchte das?“ und „Was könnte schiefgehen?“.

## 6. Capability C4 – Selbstverbesserungs-Loop

### 6.1 Ziel

Heimgewebe bewertet grob seine eigenen Maßnahmen / Policies:
„Was wir in letzter Zeit getan haben – hat das eher geholfen oder geschadet?“

### 6.2 Umsetzung (Phase 3)

**In metarepo**:
- Policy-Contracts finalisieren/vereinheitlichen (falls nötig):
  - `policy.decision.schema.json`
  - `policy.feedback.schema.json`
  - `policy.snapshot.schema.json`

**In hausKI**:
- Wenn hausKI eine „wichtige Entscheidung“ trifft (z. B. CI-Policy, WGX-Profil, automatisierte Aktion):
- Generiere ein `policy.decision` Event:
  - `decision_id`, `policy_id`, `context`, `expected_effect`.

**In wgx + CI (Fleet)**:
- WGX-Guard/Smoke-Läufe erzeugen:
  - `metrics.snapshot` Events.
  - Zusätzlich einfache Outcome-Indikatoren: z. B. `ci_status`, `error_count`, `duration`.

**In heimlern** (Kleiner „Policy-Evaluator“-Job):
- **Input:** `policy.decision` + nachfolgende `metrics.snapshot`.
- **Output:** `policy.feedback` Event mit einfachem Score (z. B. -1, 0, +1) und Begründung kurz in Textform.

**In leitstand** (Ansicht „Policy-Wirkung“):
- Liste von Policies mit grober Ampel („tendenziell hilfreich“, „neutral“, „problematisch“).

### 6.3 Risiken

- Selbstverbesserung darf Operator nicht entmündigen:
  - Policies bleiben menschlich überschreibbar.

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
