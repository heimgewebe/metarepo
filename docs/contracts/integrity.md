# Integrität im Heimgewebe

## Konzept

Integrität ist im Heimgewebe definiert als Übereinstimmung zwischen:
1.  **Behauptung** (Contracts, Dokumentation)
2.  **Produktion** (Artefakte)
3.  **Konsum** (Nachweisbare Verwendung)

Der Leitstand visualisiert diesen Status, greift aber nicht ein.

## Prinzipien

1.  **Diagnose-only**: Integritäts-Checks ändern nichts am System. Sie beobachten nur.
2.  **Keine Handlungspflicht**: Ein `FAIL` oder `MISSING` Status führt nicht zum Abbruch von CI-Pipelines.
3.  **Missing ist erlaubt**: Ein Repository, das keine Daten liefert, hat den validen Status `MISSING`. Es wird nicht "interpoliert" oder geraten.

## Integritäts-Kreislauf (The Loop)

Der Integritätsstatus fließt durch das System und bindet die Komponenten aneinander:

*   **WGX (Guard):** Erzwingt die Erzeugung und Validierung der Artefakte (`wgx guard`, `wgx integrity`). Validiert strikt gegen das Payload-Schema.
*   **semantAH (Producer):** Erzeugt den eigentlichen Bericht (`summary.json`) und den kanonischen Payload (`event_payload.json`).
*   **Plexer (Router):** Leitet das Event (`integrity.summary.published.v1`) unverändert weiter (Pass-through).
*   **Chronik (Store):** Speichert das Event als historischen Fakt. Unterscheidet zwischen Input-Event (Type top-level) und Storage/View (Type im Payload/Domain).
*   **Leitstand (Display):** Visualisiert den Status. Nutzt `payload.url` um den detaillierten Bericht (`summary.json`) zu laden.

## Contract & Semantik

### Artefakte & Kanon

*   **reports/integrity/summary.json**: Der vollständige Bericht (mensch- und maschinenlesbar). Enthält Details wie `counts`.
*   **reports/integrity/event_payload.json**: Das **kanonische, strikte Payload-Artefakt**.
    *   Muss exakt dem Schema entsprechen.
    *   Darf **keine** `counts` oder andere Zusatzdaten enthalten.
    *   Dient als "Proof of Existence" für den Bericht.
*   **reports/integrity/event.json**: Ein abgeleiteter Transport-Envelope (Convenience für CI), der den Payload umschließt.

### Payload Schema

Der Payload in `integrity.summary.published.v1` ist strikt definiert:

```json
{
  "url": "https://...",
  "generated_at": "ISO8601",
  "repo": "owner/repo",
  "status": "OK|WARN|FAIL|MISSING|UNCLEAR"
}
```

*   **Verboten:** Jegliche anderen Keys (insbesondere `counts`).
*   **Pflicht:** Alle 4 oben genannten Felder.

### URL Semantik

*   **`payload.url`** zeigt zwingend auf **`reports/integrity/summary.json`** (den Bericht).
*   Sie zeigt **nicht** auf `event_payload.json` oder `event.json`.
*   Grund: Der Leitstand nutzt diese URL, um Details ("Warum ist Status FAIL?") nachzuladen.

## Status-Werte

*   `OK`: Alles in Ordnung, Claims und Artefakte stimmen überein.
*   `WARN`: Kleinere Abweichungen, nicht kritisch.
*   `FAIL`: Kritische Diskrepanz (z.B. Contract verletzt, Artefakt fehlt).
*   `MISSING`: **Transport-Status**. Kein Bericht geliefert oder erzeugt. Darf *nicht* verwendet werden, nur weil Artefakt-Zähler 0 sind (das wäre ein valider, leerer Bericht mit Status `OK` oder `WARN`).
*   `UNCLEAR`: Status konnte nicht ermittelt werden (technischer Fehler bei der Diagnose).
