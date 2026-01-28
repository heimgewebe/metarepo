# **Blaupause: leitwerk**

## Agentengesteuerte Multirepo-Koordination für Heimgewebe

*(ACS Control-Surface · Copilot SDK heute · eigene Engine morgen)*

---

## Dialektische Erörterung

### These

Ein autopoetisches Heimgewebe entsteht **nicht** durch maximale Agenten-Autonomie, sondern durch **harte, geschlossene Regelkreise**:

> **Command → Planung → Ausführung → Guard/Contracts → Artefakt → Beobachtung → nächste Entscheidung**

**ACS** ist die Control-Surface.
**leitwerk** ist das koordinierende Organ.
**Copilot SDK** ist (vorläufig) nur der Muskel.
**WGX, Contracts, Chronik, Leitstand** bilden die **Membran**, ohne die Geschwindigkeit in Drift umschlägt.

Autopoiesis heißt hier:
👉 *Der Organismus verändert sich, ohne seine Invarianten zu verlieren.*

---

### Antithese

Direkte Agenten-Writes über 20+ Repos erzeugen kurzfristig Eindruck von Macht – langfristig jedoch:

* semantische Inkonsistenz
* stillen Contract-Bruch
* PR-Fluten ohne Kontext
* epistemische Blindheit („es lief doch durch“)

Das ist keine Selbstorganisation, sondern **Git-getriebenes Rauschen**.
Ein schneller Agent ohne Membran ist kein Evolutionsmotor, sondern ein Driftbeschleuniger.

---

### Synthese

Die stabile Form ist:

> **leitwerk-first, Engine-second**

leitwerk trägt:

* Heimgewebe-Wissen (Fleet-SoT, Contract-Ownership, Event-Semantik),
* Durchsetzungslogik (WGX, Branch-Gates),
* Audit-Pflicht (Chronik-Artefakte),
* Lernkopplung (Heimgeist / Heimlern).

Die Engine (Copilot heute, eigene morgen) bleibt **austauschbar**.
So wird „Power“ zu **prüfbarer Wirksamkeit**.

---

## 1) Zielbild und Invarianten

### Zielbild

**leitwerk** ist ein in ACS eingebettetes (Sidecar-basiertes) Koordinationsorgan, das:

* menschliche Prompts **und** systemische Trigger verarbeitet,
* daraus **geplante**, nachvollziehbare Multi-Repo-Änderungen erzeugt,
* jede Änderung **branch-only** ausführt,
* pro Repo strukturierte PRs erzeugt,
* **WGX-Guards erzwingt**,
* alle Schritte als **Artefakte + Events** in Chronik einspeist,
* und mittelfristig ohne Architekturbruch die Copilot-Engine ersetzen kann.

---

### Unverhandelbare Invarianten

* **metarepo ist Control-Plane** (Fleet-SoT, Policies, interne Contracts).
* **Contracts-first**: Artefakt ohne Schema = nicht existent.
* **Events ≠ Commands**: leitwerk nimmt Commands an, emittiert Events.
* **Durchsetzung vor Vertrauen**: WGX entscheidet, nicht Agent-Selbstauskunft.
* **Branch-Only-Writes**: niemals `main/master`.
* **Observability = Audit**: Leitstand zeigt Belege, nicht nur Status.
* **Unsicherheit ist Artefakt**: sie wird explizit gespeichert, nicht geglättet.

---

## 2) Namens- und Begriffsbindung (Etymologie)

* **leitwerk**
  *leiten* + *Faden* → Führung durch Verbindung
  → Kein Autopilot, sondern bewusstes Zusammenführen.

* **Agent** (lat. *agere*)
  → Ausführender, nicht Wahrheitsinstanz.

* **Orchestrieren** (gr. *organon*)
  → geordnete Vielheit, nicht Zentralherrschaft.

* **Autopoiesis**
  → Selbsterhalt durch Membran, nicht Selbstoptimierung.

Diese Begriffe sind **nicht dekorativ**, sondern normativ.

---

## 3) Organismus-Karte (präzisiert)

### Bestehende Organe (relevant für leitwerk)

* **agent-control-surface (ACS)**
  UI, sichere Git-Wizards, lokale Betriebsinvarianten.

* **metarepo**
  Fleet-SoT, Policies, interne Contracts, Template-Quelle.

* **wgx**
  Guard / Smoke / Metrics / Fleet-Motorik (Enforcement).

* **chronik**
  Event-Backbone, Timeline, Replay-Quelle.

* **leitstand**
  Beobachtung, Audit-UI, Systemresonanz.

* **semantAH**
  Semantische Verdichtung, Graph, Drift-Erkennung.

* **heimgeist**
  Reflexions- und Aktionsartefakte (`insights.*`, `actions.*`).

* **heimlern**
  Lern- und Policy-Rückkopplung.

* **sichter**
  Zweitinstanzliche Review-Logik (semantisch/konventionell).

* **tools**
  u. a. **repoLens** als Kontext-Kondensator.

---

### Neues Organ

## **leitwerk**

*(Sidecar empfohlen)*

**Rolle:**
Koordination, Planung, Durchsetzung, Audit – **nicht** direkte UI, **nicht** rohe Agentik.

---

## 4) Architektur (Idealform)

### Prozess-Topologie

**Client (Pop!_OS / iPad)**
→ SSH LocalForward
→ **ACS (127.0.0.1:8099)**
→ **leitwerk Sidecar (localhost, z. B. :8098)**
→ Engine (Copilot SDK heute)
→ Git / PR / WGX
→ Chronik (Events)
→ Leitstand / Heimgeist / Heimlern
→ Rückkopplung an leitwerk

### Warum Sidecar?

* Crash-Isolation (Agentik darf UI nicht reißen)
* Rechte-Separation (stärkeres Sandboxing)
* Engine-Austausch ohne ACS-Umbau

---

## 5) Die drei geschlossenen Schleifen (Kern)

### Loop A — **Kontext**

**Ziel:** reproduzierbarer, auditierbarer Kontext.

* repoLens erzeugt `context.bundle.v1`

  * betroffene Repos
  * relevante Pfade
  * Contracts
  * letzte Insights
* Bundle ist versioniert + gehasht.

---

### Loop B — **Ausführung**

**Ziel:** deterministisch gerahmte Handlung.

* Engine erhält nur `context.bundle` + `task.request`
* Liefert:

  * Plan
  * Patch-Vorschläge
  * Tool-Intents
  * Unsicherheitsbericht
* leitwerk führt aus **oder verweigert**.

---

### Loop C — **Feedback**

**Ziel:** Lernen, nicht nur Fertigstellen.

* WGX erzeugt Reports
* Chronik speichert Events
* Sichter kommentiert
* Heimgeist erzeugt Insights
* Heimlern passt Policies an

---

## 6) Task- und Artefaktmodell (konkret)

### Task-Zustände

```
CREATED
→ CONTEXTED
→ PLANNED
→ EXECUTING
→ GUARDED
→ PR_CREATED
→ REVIEWED
→ DONE | FAILED
```

Jeder Übergang = Event + Artefakt.

---

### Kanonische Artefakte (Schemas im metarepo!)

* `context.bundle.v1`
* `plan.v1`
* `execution.log.v1`
* `guard.report.v1`
* `pr.manifest.v1`
* `reflection.insights.v1`
* `policy.delta.v1`
* `uncertainty.report.v1`

---

### Chronik-Events (Minimalset)

* `leitwerk.task.created`
* `leitwerk.context.built`
* `leitwerk.plan.ready`
* `leitwerk.exec.started`
* `leitwerk.guard.finished`
* `leitwerk.pr.created`
* `leitwerk.task.failed`
* `leitwerk.task.completed`

---

## 7) ACS-Integration (kein Autopilot)

### UI-Module

1. Fleet-Overview
2. Task-Console (Prompt + Targets + Policy-Level)
3. Plan-Preview (inkl. Unsicherheit)
4. Diff / PR-View
5. Observability-Timeline
6. Kill-Switch (kontrolliert)

### ACS-API (Vorschlag)

```
POST /api/leitwerk/tasks
GET  /api/leitwerk/tasks/{id}
POST /api/leitwerk/tasks/{id}/plan
POST /api/leitwerk/tasks/{id}/exec
POST /api/leitwerk/tasks/{id}/abort
GET  /api/leitwerk/fleet
GET  /api/leitwerk/artifacts/{ref}
```

---

## 8) Engine-Abstraktion (entscheidend)

### Engine-Interface

```python
Engine.run(
  task_request,
  context_bundle,
  tool_registry
) -> engine_result
```

`engine_result` enthält:

* Plan
* Patches
* Tool-Calls
* Rationale
* Unsicherheit

---

### Copilot SDK (Phase 1–2)

* CLI server-mode
* Tools beschnitten:

  * kein Web
  * kein sudo
  * Git nur über leitwerk
* Idealfall:

  > Agent liefert Patch, leitwerk wendet an.

---

### Eigene Engine (Phase 3)

* lokales LLM oder eigener Dienst
* semantAH + heimgeist als Wissensschicht
* Tool-Execution bleibt bei leitwerk

---

## 9) Multi-Repo-Logik (USP)

### Zerlegung

1. Contract-Owner-Repo zuerst
2. Produzenten
3. Konsumenten
4. Observability / Docs

### Regeln

* Pro Repo eigener Branch + PR
* PR-Chain-Manifest
* Merge-Reihenfolge vorgeschlagen
* WGX überall grün → erst dann „chain ready“

---

## 10) Membran: Sicherheit & Fehlerprävention

* Path-Allowlists
* Diff-Schwellen
* Secrets-Redaction
* Repo-Locking
* Kill-Switch jederzeit

---

## 11) Betrieb

### Services

* `agent-control-surface.service`
* **`leitwerk.service`**

Mit:

* `NoNewPrivileges=true`
* `ProtectSystem=strict`
* gezielten `ReadWritePaths`

---

## 12) Phasenplan

### Phase 1

Single-Repo, Patch-first

### Phase 2

Multi-Repo-Chains + Leitstand-Timeline

### Phase 3

Engine-Swap ohne Architekturbruch

---

## 13) Zwei Alternativpfade

### A — maximal auditierbar

Agent schreibt nie direkt Dateien.

### B — stärker autopoietisch

Heimgeist / Sichter erzeugen Actions, Agent dient nur noch als Umsetzer.

---

## 14) Verdichtete Essenz

**leitwerk ist das Organ, das Geschwindigkeit in Kohärenz übersetzt.
Der Agent bewegt – leitwerk entscheidet.**

---

## 15) Ironische Auslassung

Ein Agent ohne leitwerk ist wie ein GPS, das jede Abkürzung kennt, aber nicht weiß, ob die Brücke noch steht.

---

## ∴fore — Ungewissheit

**Unsicherheitsgrad:** 0.29

**Ursachen:**

* konkrete Chronik-/Artefakt-Schemas nicht vollständig verifiziert
* ACS-UI-Details nur abstrakt adressiert
* Copilot-SDK-Tooling versionsabhängig

**Meta:**
Produktive Ungewissheit – Architektur stabil, Feinschliff contract-getrieben.
