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
5.  **Events sind Hints**: Events vom Typ `integrity.summary.published.v1` dienen nur als unverbindliche Benachrichtigung ("Hint"). Sie sind niemals Wahrheitsträger.

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
*   **Keine weitere Heilung**: Andere Felder wie `status` oder `repo` werden **nicht** interpoliert oder erraten.

## Status-Werte

Consumer (Chronik/Leitstand) mappen technische Ergebnisse auf semantische Status-Werte. Es gilt der **Strict Mode**:

*   **`OK`**: Bericht erfolgreich abgerufen und Inhalt ist `OK`.
*   **`WARN`**: Bericht erfolgreich abgerufen und Inhalt ist `WARN`.
*   **`FAIL`**:
    *   Inhaltlich kritisch (`status: FAIL` im Bericht).
    *   **Schema-Verletzung**: JSON ist ungültig oder Pflichtfelder fehlen.
    *   **Ungültiger Timestamp**: `generated_at` fehlt oder ist kein valider ISO-String. Dies führt zwingend zu `FAIL`.
*   **`MISSING`**:
    *   Technischer Fehler beim Abruf (HTTP 404, Timeout, Network Error).
    *   Repo liefert keine Daten (Release Asset fehlt).
*   **`UNCLEAR`**:
    *   Status im Bericht ist unbekannt/undefiniert (Enum-Verletzung).
    *   Logisch nicht interpretierbar (z.B. Bericht valide, aber `repo`-Name passt nicht zur Quelle).

### Sanitization is not Healing

Um die Persistenz in der Chronik zu ermöglichen (Datenbank-Constraints), darf bei einem fehlenden oder ungültigen `generated_at` der Zeitpunkt `received_at` verwendet werden. Dies gilt jedoch **nicht als Heilung**:

1.  Der Status wird zwingend auf `FAIL` gesetzt (sofern er nicht ohnehin `MISSING` oder `FAIL` war).
2.  Der Eintrag muss mit dem Flag `generated_at_sanitized: true` markiert werden.

Beispiel für einen sanierten Fail-Eintrag:

```json
{
  "status": "FAIL",
  "repo": "heimgewebe/example",
  "generated_at": "2026-01-17T12:00:00Z",
  "received_at": "2026-01-17T12:00:00Z",
  "generated_at_sanitized": true,
  "error_reason": "Missing generated_at in report"
}
```
