# Heimgewebe – Capability-Plan 2026 (Observatorium, Intent, Metabrain)

> Status: Plan / Orientierung
> Bezugsdoku: `docs/system/heimgewebe-zielbild.md`, `docs/system/heimgewebe-organismus.md` (falls vorhanden)

Dieses Dokument beschreibt einen schlanken, aber verbindlichen Plan,
welche **Fähigkeiten** Heimgewebe in den nächsten Ausbaustufen grob
bekommen soll – ohne neue Repositories einzuführen.

Im Fokus stehen vier Capabilities:

1. Semantisches Observatorium (C1)
2. Intent-Resolver / Intelli-Orchestrator light (C2)
3. Projekt-Metabrain / Szenarien-Layer (C3)
4. Selbstverbesserungs-Loop des Organismus (C4)

Alle Capabilities bauen auf existierenden Organen auf:

- metarepo (Contracts, Policies)
- semantAH (Wissens- & Insight-Schicht)
- mitschreiber (OS-Kontext)
- hausKI (Entscheidungs- & Orchestrierungskern)
- heimgeist (Meta-Reflexion)
- heimlern (Policy- / Bandit-Logik)
- chronik (Event-Store)
- leitstand (UI / Visualisierung)
- wgx (Fleet-Motorik, Metriken)

---

## 1. Ausgangslage

Das Zielbild des Heimgewebes ist in `docs/system/heimgewebe-zielbild.md` definiert:

- Events machen Fakten sichtbar.
- SemantAH erzeugt Bedeutung.
- HausKI entscheidet.
- Heimgeist reflektiert.
- Heimlern generalisiert.
- WGX bewegt die Fleet.
- Leitstand macht alles sichtbar.

Der aktuelle Organismus besitzt bereits:

- eine Ereignisachse (chronik, aussensensor, CI-Events)
- eine Wissensachse (semantAH, Vault-Index)
- eine Entscheidungsachse (hausKI)
- eine Fleet-/Metrikachse (wgx)
- eine OS-Kontextachse (mitschreiber)

**Es fehlen jedoch explizit modellierte Fähigkeiten für:**

- Themen- und Wissensräume (Observatorium)
- Intent-/Arbeitsmodus-Erkennung (Intelli-Orchestrator)
- Projektszenarien / Alternativenräume (Metabrain)
- Bewertung des eigenen Verhaltens (Selbstverbesserungs-Loop)

Diese Lücke soll dieser Plan schließen.

---

## 2. Leitprinzipien

1. **Contracts first**
   Jede neue Capability beginnt mit einem JSON-Schema im Metarepo.

2. **Keine neuen Repos in Phase 1**
   Wir nutzen bestehende Organe und erweitern sie um Capabilities.

3. **Events statt Seiteneffekte**
   Neue Fähigkeiten sollen Events oder Snapshots erzeugen, die in
   chronik/leitstand sichtbar werden.

4. **Minimal start, iterativ verfeinern**
   Heuristische MVPs sind erwünscht; Perfektion darf Implementierung
   nicht blockieren.

---

## 3. Capability C1 – Semantisches Observatorium

### 3.1 Ziel

Das Heimgewebe soll für Operatoren und Agenten sichtbar machen:

- Welche Themenräume sind aktuell aktiv?
- Welche Quellen (Vault, Events, Repos) speisen diese Themen?
- Welche Leitfragen ergeben sich daraus?

### 3.2 Beteiligte Repos

- metarepo
  - definiert `contracts/knowledge.observatory.schema.json`
- semantAH
  - erzeugt Observatory-Snapshots nach diesem Schema
- chronik (optional)
  - speichert Observatory-Snapshots als `event.line`
- leitstand
  - visualisiert Themenräume und Leitfragen

### 3.3 MVP – „kleines Observatorium“

**Implementationsziel:**

- Täglicher Job in semantAH, der aus:
  - ausgewählten Vault-Bereichen (vault-gewebe)
  - relevanten Events (chronik)
  heuristische Topic-Cluster erzeugt und als
  `knowledge.observatory`-Dokument ausgibt.

- Leitstand-Panel:
  - Liste von Topics mit:
    - Titel
    - Anzahl Quellen
    - einer generierten „offenen Frage“

---

## 4. Capability C2 – Intent-Resolver (Intelli-Orchestrator light)

### 4.1 Ziel

Heimgewebe soll grob erkennen, in welchem Arbeitsmodus sich der Nutzer
gerade befindet (z. B. „Coding an Repo X“, „Schreiben“, „Research“) und
dies als maschinenlesbare Intents verfügbar machen.

### 4.2 Beteiligte Repos

- metarepo
  - schärft/vereinheitlicht `contracts/os.context.intent.schema.json`
- mitschreiber
  - liefert `os.context.state` Events
- hausKI
  - erzeugt `os.context.intent` Events nach Contract
- leitstand
  - zeigt aktuellen und historischen Intent

### 4.3 MVP – „Intent light“

**Implementationsziel:**

- Simple Heuristik in hausKI:
  - mappt OS-Kontext aus mitschreiber auf wenige Intent-Typen
    (z. B. `coding`, `writing`, `research`, `browsing`).

- Generiert `os.context.intent` Events mit:
  - `intent_type`
  - `confidence`
  - `context_refs` (Repo/Datei/Fenster, soweit erkennbar)

- Leitstand-Widget:
  - Anzeige des aktuellen Intents + Basis-Zeitverlauf.

---

## 5. Capability C3 – Projekt-Metabrain / Szenarien-Layer

### 5.1 Ziel

Für ausgewählte Themenräume oder Projekte soll Heimgewebe
Alternativpfade anbieten können, z. B.:

- konservatives Szenario
- ambitioniertes Szenario
- experimentelles Szenario

mit Annahmen und Risiken.

### 5.2 Beteiligte Repos

- metarepo
  - definiert `contracts/project.scenario.schema.json`
- heimgeist
  - generiert Szenarien auf Basis von Observatorium + Kontext
- chronik
  - speichert Szenarien als Events
- leitstand
  - zeigt Szenarien pro Thema/Projekt

### 5.3 MVP – „3-Szenarien-Generator“

**Implementationsziel:**

- Heimgeist-Job:
  - nimmt ein Topic/Projekt aus dem Observatorium als Input
  - erzeugt 2–3 Szenarien nach `project.scenario` Schema
    (konservativ/ambitioniert/experimentell)
  - schreibt sie als Events nach chronik

- Leitstand-Erweiterung:
  - zu einem ausgewählten Topic die Szenarien auflisten.

---

## 6. Capability C4 – Selbstverbesserungs-Loop

### 6.1 Ziel

Heimgewebe soll sein eigenes Verhalten beobachten und grob einschätzen
können:

- Welche Policies / Automatismen waren hilfreich?
- Welche haben nur Lärm erzeugt?

### 6.2 Beteiligte Repos

- metarepo
  - verankert Policy-Contracts (`policy.decision`, `policy.feedback`, `policy.snapshot`)
- hausKI
  - erzeugt `policy.decision` Events für wichtige systemische Entscheidungen
- wgx
  - erzeugt `metrics.snapshot` + Outcome-Signale (z. B. CI-Status, Fehlerdichte)
- heimlern
  - wertet Entscheidungen ex-post aus und erzeugt `policy.feedback`
- leitstand
  - visualisiert Policy-Wirkung (Ampel / Scores)

### 6.3 MVP – „Policy-Ampel light“

**Implementationsziel:**

- hausKI annotiert ausgewählte Entscheidungen mit `policy.decision`.
- heimlern berechnet einfache Scores aus nachfolgenden Metriken
  (z. B. –1 / 0 / +1) und erzeugt `policy.feedback`.
- Leitstand zeigt eine einfache Liste:
  - Policy / Entscheidung
  - Trend (eher positiv / neutral / negativ).

---

## 7. Phasenübersicht

- **Phase 0 – Doku & Contracts**
  - dieses Dokument erstellen
  - `knowledge.observatory.schema.json`
  - `project.scenario.schema.json`
  - Intent-Contract prüfen/schärfen

- **Phase 1 – Observatorium + Intent (C1 + C2, MVP)**
  - semantAH-Job für Observatory
  - hausKI-Resolver für Intents
  - einfache Visualisierung in leitstand

- **Phase 2 – Szenarien (C3, MVP)**
  - Heimgeist-Job + Leitstand-Erweiterung

- **Phase 3 – Selbstverbesserungs-Loop (C4, MVP)**
  - Policy-Events + Feedback-Pipeline

---

## 8. Risiken & Trade-offs

- **Überlastung**
  Zu viele Capabilities gleichzeitig könnten zu halbfertigen Features führen.
  → Empfehlung: C1 + C2 strikt vor C3 + C4 priorisieren.

- **Semantik-Komplexität**
  Observatorium und Szenarien können schnell in Modell-Perfektionismus
  kippen.
  → MVPs bewusst heuristisch halten und später verfeinern.

- **Selbstoptimierung vs. Operator-Kontrolle**
  Automatische Policy-Anpassungen dürfen Operatoren nicht entmündigen.
  → Policy-Änderungen bleiben an Git/CI gebunden, Feedback ist zunächst
    nur Empfehlung.

---

## 9. Essenz

- Heimgewebe bekommt vier neue Fähigkeiten:
  - Themenräume,
  - Intenterkennung,
  - Projektszenarien,
  - Selbstbewertung.
- Sie bauen auf bestehenden Organen auf und werden über Contracts im
  Metarepo verankert.
- Dieses Dokument dient als Referenzpunkt für Implementierung,
  Priorisierung und Diskussion.
