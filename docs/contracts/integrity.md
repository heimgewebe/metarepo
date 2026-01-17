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

*   **WGX / Producer**: Erzeugt den Integritätsbericht (`reports/integrity/summary.json`) und veröffentlicht ihn als Release Asset.
*   **Metarepo (Constitution)**: Definiert die Liste der zu prüfenden Quellen in `reports/integrity/sources.v1.json` (Contract: `contracts/integrity.sources.v1.schema.json`).
*   **Chronik (Orchestrator)**: Liest die Quellenliste, ruft periodisch die Berichte ab, validiert und speichert den aktuellen Status.
*   **Leitstand (Display)**: Visualisiert den von der Chronik bereitgestellten Status.

## Contract & Semantik

### Artefakte & Kanon

*   **`reports/integrity/summary.json`**: Der Erzeugungspfad des Berichts im Repository.
*   **Release Asset `summary.json`**: Das Publikationsartefakt.
    *   Der Bericht muss als Datei `summary.json` unter dem Release-Tag **`integrity`** veröffentlicht werden.
    *   Die `summary_url` in der Quellenliste zeigt auf dieses Asset.
*   **`reports/integrity/sources.v1.json`**: Die **Single Source of Truth (SoT)** für Integritätsquellen.
    *   Wird generiert aus der Fleet-Definition (`fleet/repos.yml`).
    *   Schema: `contracts/integrity.sources.v1.schema.json`.

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

*   `url` ist optional im Bericht. Die Chronik ergänzt dieses Feld ("Backfilling") basierend auf der Abruf-Quelle.
*   **Keine weitere Heilung**: Andere Felder wie `generated_at`, `status` oder `repo` werden **nicht** interpoliert oder erraten.
*   Weitere Felder (wie `counts`, `details`) sind erlaubt und erwünscht für Debugging, werden aber für den High-Level-Status nicht zwingend benötigt.

## Status-Werte

Consumer (Chronik/Leitstand) mappen technische Ergebnisse auf semantische Status-Werte. Es gilt der **Strict Mode**:

*   **`OK`**: Bericht erfolgreich abgerufen und Inhalt ist `OK`.
*   **`WARN`**: Bericht erfolgreich abgerufen und Inhalt ist `WARN`.
*   **`FAIL`**:
    *   Inhaltlich kritisch (`status: FAIL` im Bericht).
    *   **Schema-Verletzung**: JSON ist ungültig oder Pflichtfelder fehlen.
    *   **Ungültiger Timestamp**: `generated_at` fehlt oder ist kein valider ISO-String.
    *   *Sanitization*: Die Chronik darf zur Persistenz `generated_at` auf `received_at` setzen, muss dies aber mit dem Flag `generated_at_sanitized: true` markieren. Der Status bleibt `FAIL` (oder wird entsprechend der Severity-Policy bewertet), da die Integrität der Quelle verletzt ist.
*   **`MISSING`**:
    *   Technischer Fehler beim Abruf (HTTP 404, Timeout, Network Error).
    *   Repo liefert keine Daten (Release Asset fehlt).
*   **`UNCLEAR`**:
    *   Status im Bericht ist unbekannt/undefiniert (Enum-Verletzung).
    *   Logisch nicht interpretierbar (z.B. Bericht valide, aber `repo`-Name passt nicht zur Quelle).
