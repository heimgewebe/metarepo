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

## Artefakte

*   **integrity.summary.json**: Ein pro Repository erzeugtes JSON-Artefakt, das den aktuellen Status zusammenfasst.
*   **integrity.summary.published.v1**: Das Event, das signalisiert, dass ein neuer Bericht verfügbar ist.

## Status-Werte

*   `OK`: Alles in Ordnung, Claims und Artefakte stimmen überein.
*   `WARN`: Kleinere Abweichungen, nicht kritisch.
*   `FAIL`: Kritische Diskrepanz (z.B. Contract verletzt, Artefakt fehlt).
*   `MISSING`: Keine Daten verfügbar (z.B. Repo liefert keinen Bericht).
*   `UNCLEAR`: Status konnte nicht ermittelt werden (technischer Fehler bei der Diagnose).
