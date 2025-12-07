# Heimgewebe Contracts – Überblick

Dieses Dokument beschreibt die Rolle der **kanonischen Contracts** im metarepo
und welche Repos sie konsumieren. Es ist der menschliche Blick auf dieselben
Informationen, die in `contracts/consumers.yaml` für Tools gebündelt sind.

## Grundprinzip

- Alle hier beschriebenen Contracts liegen kanonisch im **metarepo**.
- Consumer-Repos dürfen diese Contracts nicht eigenmächtig ändern.
- Spezialisierungen entstehen über neue Schemas, nicht über stille Forks.

Zur maschinenlesbaren Übersicht siehe:

```text
contracts/consumers.yaml
```

---

## Event-Backbone

Kern der Heimgewebe-Ereigniskette.

- `contracts/aussen.event.schema.json`
- `contracts/event.line.schema.json`
- `contracts/chronik-fixtures.schema.json`

**Typische Flüsse:**

- `aussensensor` produziert `aussen.event` und validiert gegen das kanonische Schema.
- `chronik` ingestiert `aussen.event` und legt sie als `event.line` ab.
- Fixtures für Tests nutzen `chronik-fixtures`.

---

## Metrics & Fleet

- `contracts/fleet.health.schema.json`
- `contracts/insights.daily.schema.json`

**Rollen:**

- `wgx` erzeugt und sammelt `fleet.health` als Zustandsbild der Fleet.
- `leitstand` und Auswertungen (z. B. semantAH) konsumieren diese Daten.
- `insights.daily` dient als standardisierter Exportpfad für aggregierte Einsichten.

---

## OS-Kontext & Embeddings

- `contracts/os.context.state.schema.json`
- `contracts/os.context.text.embed.schema.json`

**Rollen:**

- `mitschreiber` schreibt laufenden OS- und App-Kontext als `os.context.state`.
- `semantAH` nutzt `os.context.text.embed`, um Texte konsistent einzubetten.

---

## Policy & Entscheidungen

- `contracts/policy.decision.schema.json`
- `contracts/policy.feedback.schema.json`
- `contracts/policy.snapshot.schema.json`

**Rollen:**

- `heimlern` trifft Entscheidungen und produziert `policy.decision` sowie Feedback.
- `hausKI` konsumiert diese als Steuerungsinput.
- `policy.snapshot` dient als persistierter Zustand (z. B. für Bandits oder Lernstände).

---

## Weltgewebe-Domain (Konversationen, Knoten, Kanten)

Die feinere Ausarbeitung liegt in den jeweiligen Domain-Repos, aber die
kanonischen Contracts im metarepo definieren die gemeinsame Basis für:

- Gesprächsbezüge (`conversation`, `message`)
- Wissensknoten (`node`, `edge`)
- Rollenmodelle (`role`)

Diese Contracts sind insbesondere für:

- `semantAH` (Graph, Embeddings),
- `weltgewebe` (API),
- sowie Analyse- und UI-Schichten (`leitstand`, `heimgeist`)

relevant.

---

## Regeln für Änderungen

1. Änderungen an diesen Schemas erfolgen ausschließlich im **metarepo**.
2. Consumer-Repos können sie spiegeln, müssen aber CI-Driftchecks einsetzen.
3. Breaking Changes brauchen mindestens:
   - Dokumentation der Änderung,
   - Migrationspfad,
   - klare Versionierung (Semantik der Felder, nicht nur Dateiname).
