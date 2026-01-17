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
4.  **Pull-based**: Die Aggregation erfolgt durch aktives Abrufen (Pull) durch die Chronik, nicht durch Events (Push).

## Integritäts-Kreislauf (The Loop)

Der Integritätsstatus wird aktiv gesammelt:

*   **WGX / Producer**: Erzeugt den Integritätsbericht (`summary.json`) und veröffentlicht ihn an einer kanonischen URL (Release Asset).
*   **Metarepo (Constitution)**: Definiert die Liste der zu prüfenden Quellen in `reports/integrity/sources.v1.json`.
*   **Chronik (Orchestrator)**: Liest die Quellenliste, ruft periodisch die Berichte ab, validiert und speichert den aktuellen Status.
*   **Leitstand (Display)**: Visualisiert den von der Chronik bereitgestellten Status.

## Contract & Semantik

### Artefakte & Kanon

*   **`summary.json`**: Der vollständige Bericht.
    *   Muss als **Release Asset** unter dem Tag **`integrity`** veröffentlicht werden.
    *   Alternativ: Stabil erreichbare URL (z.B. Raw GitHub Content), wenn in `sources.v1.json` konfiguriert.
*   **`reports/integrity/sources.v1.json`**: Die **Single Source of Truth (SoT)** für Integritätsquellen.
    *   Wird generiert aus der Fleet-Definition (`fleet/repos.yml`).
    *   Definiert für jedes Repo die `summary_url`.

### Quellen-Liste (SoT)

Das Metarepo stellt die Liste aller erwarteten Integritäts-Quellen bereit:

```json
{
  "apiVersion": "integrity.sources.v1",
  "generated_at": "ISO8601",
  "sources": [
    {
      "repo": "heimgewebe/wgx",
      "summary_url": "https://github.com/heimgewebe/wgx/releases/download/integrity/summary.json",
      "enabled": true
    }
  ]
}
```

### Bericht Schema (summary.json)

Der abgerufene Bericht muss mindestens folgende Felder enthalten, um von der Chronik akzeptiert zu werden:

```json
{
  "generated_at": "ISO8601",
  "status": "OK|WARN|FAIL|MISSING|UNCLEAR",
  "repo": "owner/repo"
}
```

*   `url` ist optional im Bericht (wird von Chronik ergänzt, falls fehlend).
*   Weitere Felder (wie `counts`, `details`) sind erlaubt und erwünscht für Debugging, werden aber für den High-Level-Status nicht zwingend benötigt.

## Status-Werte

*   `OK`: Alles in Ordnung.
*   `WARN`: Kleinere Abweichungen.
*   `FAIL`: Kritische Diskrepanz oder Schema-Verletzung beim Abruf.
*   `MISSING`: Bericht konnte technisch nicht abgerufen werden (404, Network Error).
*   `UNCLEAR`: Inhaltlich nicht interpretierbar.
