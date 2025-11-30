# Heimgewebe · Vision & Architekturüberblick

## Leitidee
Heimgewebe ist ein **selbstlernendes, lokal-erstes System** zur Erleichterung, Erklärung und Verbesserung des Lebensalltags.
Es besteht aus vernetzten Repositories, die gemeinsam ein lernfähiges Ökosystem bilden – ein digitales Nervensystem für Wahrnehmung, Entscheidung und Handlung.

> **Prinzip:** Wahrnehmen → Verstehen → Entscheiden → Handeln → Reflektieren

---

## Ziele
- **Wissensmanagement**: semantische Ordnung und Verknüpfung eigener Inhalte.
- **Selbsterkenntnis**: aus Routinen, Texten, Audio und Systemdaten lernen.
- **Kommunikationserleichterung**: Schnittstellen und Tools vereinfachen Abläufe.
- **PC-Verwaltung & Automatisierung**: stabile lokale Steuerung, Monitoring, Backups.
- **Musik & Audiointegration**: kreative Tätigkeiten mit technischen Prozessen verbinden.
- **Weltverbesserung (indirekt)**: Synergien mit außenliegenden Projekten (z. B. weltgewebe).

---

## Architektur · Repos & Rollen

| Schicht | Repo | Funktion |
|----------|------|-----------|
| **Meta / Kontrolle** | **metarepo** | Zentrale Steuerzentrale: Regeln, CI-Workflows, Templates, **Contracts (Schemas)** für Datenaustausch. |
| **Motorik & Systemzustand** | **wgx** | Führt Wartung, Backups, Updates aus. Liefert periodisch **Metrics-Snapshots**. |
| **Kern / Innenwelt-KI** | **hausKI** | Orchestriert Prozesse, speichert Zustände (lokal), führt Playbooks aus, loggt Ereignisse (`events/*.jsonl`). |
| **Lernen & Policies** | **heimlern** | Rust-Lib für adaptive Entscheidungslogik; liefert `action`, `score`, `why`. |
| **Wissen & Bedeutung** | **semantAH** | Ingest von Vault-Daten, Embeddings, tägliche **Insights** (`insights/today.json`). |
| **Audio & Musik** | **hausKI-audio** | Erfasst Sessions, Latenzen, Routing; Events für „Musik“-Panel und Lernkontext. |
| **Persistenz / Audit** | **chronik** | Event-Ingest, Persistenz und Audit-Trails. Das „Gedächtnis" des Systems. |
| **Visualisierung / UI** | **leitstand** | Panels für Systemzustände, Lernfortschritt, Audioaktivität, Außenfeeds. Der „Kontrollraum". |
| **Außenwahrnehmung** | **aussensensor** | Aggregiert externe Quellen (News, Projekte, Sensorik) zu kuratiertem Feed (`export/feed.jsonl`). |
| **Werkzeuge** | **tools** | Gemeinsame Skripte und Utilities für die gesamte Flotte. |

---

## Kooperative Nachbarschaft (außerhalb der Heimgewebe-Sphäre)

| Repo | Rolle |
|------|--------|
| **weltgewebe** | Kartenbasiertes Gemeinschaftsinterface zur Verwaltung gemeinschaftlicher Güter. **Kein direkter Bestandteil** des Heimgewebes, aber wechselseitig bereichernd durch Entwicklungserkenntnisse. |

---

## Zentrale Prinzipien
- **Lokal-first**: Datenverarbeitung primär auf dem eigenen Gerät.
- **Append-only Events**: Jede Änderung erzeugt ein Ereignis, keine Überschreibungen.
- **Verträge statt Kopplung**: Repos kommunizieren ausschließlich über definierte JSON-Schemas aus `metarepo/contracts/`.
- **Explainability**: Jede Entscheidung hat ein `why`.
- **Selbstverbesserung**: heimlern lernt aus Feedback-Schleifen.
- **Transparenz & Wiederaufbau**: Insights & Indizes sind rekonstruierbar.

---

## Lernzyklus (Organismus-Analogie)

1. **Perception** – semantAH, wgx, audio, aussensensor erfassen Daten.
2. **Plan** – hausKI fragt heimlern: „Was soll ich tun?“
3. **Act** – hausKI oder wgx führen aus.
4. **Reflect** – Outcomes werden zu Events; heimlern lernt.
5. **Explain** – leitstand (UI) zeigt, *was*, *warum* und *mit welchem Ergebnis* passiert ist.

---

## Entwicklungsstrategie
1. **Verträge etablieren** (Contracts v1 im metarepo).
2. **chronik + aussensensor** → End-to-End-Flow: Außen → Innen (Ingest).
3. **leitstand** → UI für Visualisierung und Erklärung.
3. **hausKI + heimlern** → Entscheidungs- und Feedback-Mechanik.
4. **semantAH + hausKI-audio** → Wissens- und Kreativintegration.
5. **ADR-Dokumentation** fortlaufend für alle Architekturentscheidungen.

---

## Ausblick
Das Heimgewebe entwickelt sich zu einem **autonom lernenden System**,
das lokale Daten in Bedeutung übersetzt, Entscheidungen begründet und Aktionen ausführt –
transparent, nachvollziehbar und stets erklärbar.

> **Essenz:** semantAH liefert Sinn, hausKI entscheidet, heimlern verbessert, wgx handelt, chronik persistiert, leitstand erklärt, aussensensor beobachtet.
> weltgewebe bleibt als Nachbar – verbunden im Geist, nicht im Code.

---

## Diagramm

Eine visuelle Übersicht befindet sich in [heimgewebe-architektur.mmd](./heimgewebe-architektur.mmd):

%%{init: {'theme':'neutral'}}%%
graph TD
    M[metarepo]
    WGX[wgx]
    HKI[hausKI]
    HLA[heimlern]
    SEM[semantAH]
    AUD[hausKI-audio]
    CHR[chronik]
    LST[leitstand]
    AUS[aussensensor]
    WELT[weltgewebe]

    M --> WGX
    M --> HKI
    M --> CHR
    M --> LST
    WGX --> HKI
    HKI --> HLA
    HKI --> CHR
    HKI --> SEM
    HKI --> AUD
    HLA --> HKI
    SEM --> HKI
    AUD --> HKI
    AUS --> CHR
    CHR --> LST
    WELT -. know-how .-> AUS
    AUS -. insights .-> WELT

---

## Datenfluss (Contracts)

Siehe [heimgewebe-dataflow.mmd](./heimgewebe-dataflow.mmd).
Die wichtigsten Artefakte & Verträge:
- **semantAH → hausKI/chronik**: `insights/today.json`
  Schema: `contracts/insights.schema.json`
- **wgx → hausKI**: `metrics.json` (Snapshot)
  Schema: `contracts/metrics.snapshot.schema.json` (Validierung in hausKI vor Persistenz)
- **hausKI-audio → hausKI/chronik**: `audio.session_*`, `audio.latency_ms`
  Schema: `contracts/audio.events.schema.json`
- **aussensensor → chronik**: `export/feed.jsonl` → POST `/ingest/aussen`
  Schema: `contracts/aussen.event.schema.json`
- **hausKI (intern/Export)**: `~/.hauski/events/YYYY-MM.jsonl` (append-only)
  Schema: `contracts/event.line.schema.json`
- **heimlern ↔ hausKI**: `decide(ctx) → {action, score, why}` & `feedback(reward)`
  Schema: `contracts/policy.decision.schema.json`
---
## Canvas-Visualisierungen
Für eine visuelle Darstellung siehe:
- [Heimgewebe Architektur (Canvas)](./canvas/heimgewebe-architektur.canvas)
- [Heimgewebe Datenfluss (Canvas)](./canvas/heimgewebe-dataflow.canvas)

Diese Canvas-Dateien sind in **Obsidian direkt darstellbar** (Datei → Öffnen mit Canvas).
