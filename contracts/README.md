# Contracts: Single Source of Truth

Das `metarepo` ist die **einzige Quelle der Wahrheit (Single Source of Truth)** für alle internen Organismus-Contracts.

*   **Owner:** `metarepo` (hier werden Contracts definiert).
*   **Mirror:** `contracts-mirror` dient **nur** als Spiegel für externe APIs (z. B. Protobuf, abgeleitete JSONs) und darf keine internen Contracts definieren.

## Struktur

Contracts liegen flach in diesem Verzeichnis oder in thematischen Unterordnern (z. B. `epistemic/`, `events/`).

## Versionierung

Alle Contracts müssen versioniert sein: `*.vN.schema.json` (z. B. `decision.outcome.v1.schema.json`).

## Payload vs. Envelope

Wir unterscheiden strikt zwischen:

1.  **Envelope (Umschlag):** Transport-Informationen (Wer, Wann, Wo).
    *   Definiert in `event.line.schema.json` oder `heimgeist.insight.v1.schema.json` (Wrapper).
2.  **Payload (Inhalt):** Die fachliche Datenstruktur.
    *   Definiert in spezifischen Schemas wie `decision.outcome.v1.schema.json`.

**Regel:** Ein Payload-Schema (z. B. `decision.outcome`) sollte keine Envelope-Daten (wie `mq_headers`, `routing_key`) enthalten, sondern nur die fachlichen Daten. Envelope-Schemas referenzieren Payloads oder binden sie ein.

## Producers & Consumers

Die Produzenten und Konsumenten sind in den JSON-Schemas per `x-producers` und `x-consumers` Metadaten dokumentiert.

### Wichtige Akteure

*   **heimlern:** Produziert `policy.weight_adjustment` (Vorschlag). Konsumiert `decision.outcome`, `policy.weight_change.applied`.
*   **hausKI:** Produziert `decision.outcome`, `policy.weight_change.applied` (Handlung). Konsumiert `policy.decision`, `policy.weight_adjustment`.
*   **chronik:** Speichert alle Events (Event-Store).
*   **semantAH:** Analysiert Semantic-Drift.
*   **metarepo:** Definiert die Contracts (Owner).
