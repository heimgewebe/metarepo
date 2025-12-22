# Contracts-Index des Heimgewebes

Dieses Dokument listet die wichtigsten und derzeit aktiv genutzten Daten-Contracts des Heimgewebes und verknüpft sie mit den jeweiligen Repositories.

**Hinweis:** Dies ist ein kuratierter Einstiegspunkt, der keinen Anspruch auf Vollständigkeit erhebt, sondern die systemweit relevanten Contracts hervorhebt.

Ziel:

- ein **zentraler Blick** auf alle strukturbildenden Schemas,
- klare Zuordnung: *welches Repo spricht welchen Contract*,
- Grundlage für **Codegeneration**, **Validierung** und **Review-Automatisierung**.

Die Details der Schemas liegen immer in den jeweiligen Dateien (JSON-Schema, Protobuf, YAML).
**Quelle der Wahrheit ist immer das jeweilige Repo, nicht dieses Dokument.**

---

## 1. Zentrale Contracts im metarepo

Diese Schemas sind der „Verfassungskern“ des Heimgewebes.
Sie liegen (sofern nicht anders angegeben) in `contracts/*.schema.json` im **metarepo**.

### 1.1 Event-Backbone

- `event.line.schema.json`
  - Zweck: generischer Event-Stream-Contract (Basis für chronik, Leitstand, HausKI-Logs, usw.).
- `aussen.event.schema.json`
  - Zweck: standardisierte Außen-Events, bevor sie in die interne Event-Landschaft aufgenommen werden.
- `audio.events.schema.json`
  - Zweck: Audio-bezogene Ereignisse (z. B. Aufnahmen, Transkriptionen, TTS).
- `intent.event.schema.json`
  - Zweck: Intent-Events aus Audio/Text für chronik/hausKI (Intent-Erkennung mit Confidence).

### 1.2 Fleet & Metriken

- `fleet.health.schema.json`
  - Zweck: Health-Status der Repos/Services, inkl. `details[]` pro Einheit.
- `metrics.snapshot.schema.json`
  - Zweck: Metrik-Snapshots (Messpunkte für Zustand / Performance).

### 1.3 Insights & semantische Ebene

- `insights.schema.json`
  - Zweck: generische „Insight“-Einträge (Erkenntnisse, Beobachtungen, Analysen).
- `insights.daily.schema.json`
  - Zweck: tägliche, verdichtete Insights mit `topics`, `source`, `metadata`.
- `knowledge.graph.schema.json`
  - Zweck: generisches Wissensgraph-Schema (Knoten, Kanten, Beziehungen).
- `knowledge.observatory.schema.json`
  - Zweck: Snapshot des semantischen Observatoriums mit aktiven Themenräumen, Quellen, Signalen, Leitfragen, blinden Flecken und verworfenen Hypothesen.
  - Produzent: semantAH
  - Konsumenten: leitstand, hausKI, heimlern
  - Typ: Beobachtung

### 1.4 Policy-Kreislauf

- `decision.preimage.schema.json`
  - Zweck: expliziter Erkenntnis-Vorlauf vor einer wirksamen Entscheidung – dient Auditierbarkeit, Lernfähigkeit und Sichtbarkeit von Unsicherheit/Alternativen.
- `policy.decision.schema.json`
  - Zweck: formalisierte Entscheidungen (wer/was hat entschieden, mit welcher Option).
- `policy.feedback.schema.json`
  - Zweck: Feedback zu Entscheidungen (Erfolg, Fehler, Korrekturen).
- `policy.snapshot.schema.json`
  - Zweck: momentane Policy-Konfiguration im zeitlichen Verlauf (Versionierung des Regelwerks).

### 1.5 OS-Kontext & Embeddings

- `os.context.state.schema.json`
  - Zweck: aktueller Kontextzustand eines „Heimgewebe-OS“ (Umgebung, Sessions, aktive Knoten).
- `os.context.intent.schema.json`
  - Zweck: Absichten/Intents, die vom System erkannt oder gesetzt werden.
- `os.context.text.embed.schema.json`
  - Zweck: Texte, die eingebettet (Vektorraum) werden sollen.
- `os.context.text.redacted.schema.json`
  - Zweck: bereinigte / geschwärzte Textvarianten für Privacy.

### 1.6 Agenten, Werkzeuge & Workflows

- `agent.tool.schema.json`
  - Zweck: Beschreibung von Tools, die ein Agent nutzen kann (Name, Eingaben, Ausgaben).
- `agent.workflow.schema.json`
  - Zweck: Beschreibung von Workflows / Pipelines, die ein Agent ausführen kann.
- `dev.tooling.schema.json`
  - Zweck: Struktur für Dev-Tooling-Informationen (z. B. Toolchain-Definitionen, Checks).

### 1.7 Review-Policies

- `review.policy.yml`
  - Zweck: Richtlinien für Reviews (z. B. Sichter, heimgeist), dient als semantische Grundlage für automatisierte Bewertung.

### 1.8 Planung & Szenarien

- `project.scenario.schema.json`
  - Zweck: Beschreibung alternativer Pfade für ein Thema oder Projekt (konservativ, ambitioniert, experimentell) mit Annahmen, Risiken und vorgeschlagenen Aktionen.
- `consumers.yaml`
  - Zweck: Maschinenlesbare Übersicht, welche Repos welche zentralen Heimgewebe-Contracts konsumieren (Modus: reference-only oder mirror) – quer über alle Contract-Kategorien hinweg.

---

## 2. Contracts-Repo (offizielle APIs)

Repository: **heimgewebe/contracts-mirror**

### 2.1 Protobuf-APIs

- `heimgewebe/aussen/v1/event.proto`
  - Contract: `EventEnvelope`
  - Zweck: API-Contract für Außen-Events (id, event_type, occurred_at, payload, context).
- `heimgewebe/heimlern/v1/decision.proto`
  - Contract: `Decision`
  - Zweck: Entscheidungen aus Sicht von heimlern (decision_id, learner_id, Optionen, decided_at, metadata).

### 2.2 JSON-Schema-Mirror

- `json/aussen.event.schema.json`
- `json/os.context.state.schema.json`
- `json/test.schema.json`

Zweck:

- JSON-Repräsentationen der Protobuf-Schnittstellen,
- Grundlage für Tests, Beispielpayloads, clientseitige Validierung.

---

## 3. Repo-spezifische Contracts

### 3.1 hausKI

Repository: **heimgewebe/hausKI**

- `docs/contracts/events.schema.json`
  - Zweck: HausKI-Event-Contract (Logging, Bus, Audits).
- `docs/contracts/tools/query_vault.schema.json`
- `docs/contracts/tools/search_codebase.schema.json`
  - Zweck: Tool-Eingabe-Contracts für spezifische HausKI-Tools.

### 3.2 aussensensor

Repository: **heimgewebe/aussensensor**

- `contracts/aussen.event.schema.json`
  - Zweck: lokale Variante des Außen-Event-Contracts für Sensor-Ingest, bevor die Events an chronik / heimlern weitergereicht werden.

### 3.3 semantAH

Repository: **heimgewebe/semantAH**

- `contracts/insights.schema.json`
  - Zweck: generische Insight-Struktur (in semantAH-Kontext).
- `contracts/semantics/node.schema.json`
- `contracts/semantics/edge.schema.json`
- `contracts/semantics/report.schema.json`
  - Zweck: Graph-Contract des semantischen Blutkreislaufs (Knoten, Kanten, Reports).
- `contracts/semantics/examples/*`
  - Zweck: valid/invalid Beispiele, direkt für Tests und für LLM-Kontext verwendbar.

### 3.4 heimlern

Repository: **heimgewebe/heimlern**

- `contracts/aussen_event.schema.json`
- `contracts/policy.decision.schema.json`
- `contracts/policy_feedback.schema.json`
- `contracts/policy_snapshot.schema.json`

Zweck:

- domänenspezifische Ausprägung des Policy-Kreislaufs,
- strukturiertes Decision- und Feedback-Logging,
- Grundlage für lernende Policies.

### 3.5 weltgewebe

Repository: **heimgewebe/weltgewebe**

- `contracts/domain/conversation.schema.json`
- `contracts/domain/message.schema.json`
- `contracts/domain/node.schema.json`
- `contracts/domain/edge.schema.json`
- `contracts/domain/role.schema.json`
- `contracts/domain/examples/*.json`

Zweck:

- Datenmodell für Gesprächsräume, Nachrichten, Rollen und semantische Knoten,
- Grundgerüst für alles, was „Gespräch als Datenstruktur“ versteht.

### 3.6 mitschreiber

Repository: **heimgewebe/mitschreiber**

- `contracts/os.context.text.embed.schema.json`

Zweck:

- spezialisierter Contract für Texte, die eingebettet werden (z. B. Mitschriften, Notizen).

---

## 4. Neuen Contract anlegen – Minimalvorlage

Für neue JSON-Schemas im Heimgewebe sollte sich an folgendem Muster orientiert werden
(vereinfacht, **tatsächliche Konventionen siehe `contracts/SCHEMA_CONVENTIONS.md` im contracts-mirror-Repo**):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.heimgewebe.de/<bereich>/<name>.schema.json",
  "title": "<Kurzer Name>",
  "description": "<Knappe Beschreibung des Zwecks>",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Stabile, systemweite ID"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
    // weitere Felder …
  },
  "required": ["id", "created_at"],
  "additionalProperties": false
}
```

Grundsätze:

- **Eindeutige `$id`** je Contract,
- **klare `title` und `description`**,
- **`additionalProperties: false`**, außer es gibt gute Gründe für Offenheit,
- gemeinsame Stammdaten-Felder (`id`, `created_at`, ggf. `source`, `trace_id`) möglichst wiederverwenden.

---

## 5. Pflege dieses Dokuments

Dieses Dokument wird kuratiert gepflegt, um systemweit relevante Contracts sichtbar zu halten:

- **Zentrale metarepo-Contracts:** Wenn neue Dateien unter `contracts/*.schema.json` angelegt, umbenannt oder gelöscht werden, sollte dieses Dokument in derselben PR aktualisiert werden.
- **Repo-spezifische Contracts:** Änderungen an Contracts in anderen Repos sollten hier referenziert werden, falls sie systemweit relevant sind (z. B. Events, Policy-Strukturen, Weltgewebe-Domänenmodelle).
- **Qualitätssicherung:** Ein automatischer Guard-Check (siehe `.github/workflows/contracts-index-guard.yml`) prüft, dass alle zentralen `contracts/*.schema.json`-Dateien im Index vorkommen.

Weitere Hinweise zur Contracts-Pflege finden sich in `CONTRIBUTING.md`.

---

## 6. Nutzung für KI & Tools

Für KIs und Tools kann dieses Dokument als Einstiegsindex dienen:

- *Welche Contracts gibt es?*
- *In welchem Repo liegen sie?*
- *Welches Schema ist für welchen Datenstrom zuständig?*

Die eigentlichen Schemas sollten bei Bedarf immer direkt aus den Repositories geladen oder aus dem jeweiligen Merge-Kontext entnommen werden.
