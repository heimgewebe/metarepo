# Sichter – Contract Overview

Sichter ist der präzise Werkzeugkasten für automatisierte Qualitätsreflexion innerhalb des Heimgewebes. Er reagiert auf `repository_dispatch`-Events und führt Analysen mit deterministischer Struktur durch.

## Ereignis: heimgewebe-command

### Payload (vereinfacht):

```json
{
  "repo": "heimgewebe/<zielrepo>",
  "run_id": "<run>",
  "command": "<string>",
  "context": {
    "pr": "<nummer oder null>",
    "file": "<optional datei>",
    "args": {}
  }
}
```

### Antwortstruktur

```json
{
  "status": "ok" | "error",
  "analysis": {
    "summary": "<kurze Einschätzung>",
    "details": "<markdown-html-fähiger Text>",
    "actions": [
      {
        "suggestion": "<konkrete Handlung>",
        "risk": "<niedrig/mittel/hoch>"
      }
    ]
  }
}
```

## Hauptfunktionen

- `quick_analysis`: leichte Heuristik, semantisch + syntaktisch
- `deep_analysis`: vollständiger Durchgang inkl. CI-Hilfsmodulen
- `file_focus`: targeted Analyse einzelner Dateien
- `risk_vector`: heuristische Bewertung von Einfluss, Drift, Redundanz

## Grundprinzipien

1. Keine direkte Ausführung gefährlicher Aktionen.
2. Immer Markdown-Antwort für Rückkopplung an PR.
3. Alle Analysen deterministisch, reproducible.
4. Nutzung von semantAH, wenn verfügbar.
5. Sichter ist ein Tool, keine Meta-Instanz – das ist Heimgeist.
