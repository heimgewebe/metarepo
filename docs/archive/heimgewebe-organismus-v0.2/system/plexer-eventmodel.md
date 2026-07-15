# Plexer – Ereignisnetz für Heimgewebe

Plexer ist der Event-Router des Heimgewebe-Organismus.
Er verbindet Repos, Workflows und Dienste über ein einheitliches Ereignismodell.

Ziele:

- ein einheitliches Event-Format für alle Heimgewebe-Repos
- ein klarer, austauschbarer Event-Router (Plexer)
- saubere Trennung von:
  - *Transport* (Plexer)
  - *Interpretation* (Heimgeist, semantAH, weitere Konsumenten)

## Event-Grundformat (v1)

Alle Events, die Plexer entgegen nimmt, folgen diesem Minimalformat:

```json
{
  "type": "ci.result",
  "source": "heimgewebe/<repo>",
  "timestamp": "2025-11-30T12:34:56Z",
  "correlation_id": "optional-id",
  "payload": {
    "status": "success",
    "details": {}
  }
}
```

Pflichtfelder:

- `type`: logischer Eventtyp (z. B. `ci.result`, `deploy.failed`, `incident.detected`)
- `source`: Ursprung (Name des Repos oder Dienstes)
- `payload`: beliebiges JSON-Objekt mit typ-spezifischen Details

Optionale Felder:

- `timestamp`: ISO-8601, falls nicht gesetzt, kann Plexer den Empfangszeitpunkt eintragen
- `correlation_id`: dient zur Korrelation von mehreren Events (z. B. zwischen CI, Review und Deployment)

## Wichtige Eventtypen (Startset)

Dieses Eventmodell ist bewusst klein und erweiterbar gehalten.
Empfohlene Typen für v1:

- `ci.result`
  - Ergebnis eines CI-/WGX-Laufs (Status, Dauer, betroffene Branch/PR)
- `pr.reviewed`
  - Review-Ergebnis aus Sichter oder manuellen Reviews
- `deploy.started` / `deploy.succeeded` / `deploy.failed`
  - Deployment-Status
- `incident.detected`
  - Meldung eines Vorfalls (z. B. Monitoring-Alarm)

Genaue Payloads pro Typ können in eigenen Schemas ergänzt werden, sobald Plexer stabil läuft.

## Rollenverteilung

- **metarepo**
  - hält diese Dokumentation
  - definiert die Schemas (in einem späteren Schritt)
  - liefert GitHub-Workflow-Templates zum Versenden von Events

- **plexer**
  - nimmt Events über HTTP entgegen (`POST /events`)
  - prüft Minimalstruktur (`type`, `source`, `payload`)
  - loggt Events
  - leitet Events an Heimgeist (und andere Konsumenten) weiter

- **heimgeist**
  - wertet Events aus
  - baut daraus:
    - Risiko-Modelle
    - Epics / Patterns
    - Empfehlungen und Aktionen

## Nächste Ausbaustufen

- Versionierte JSON-Schemas für alle Eventtypen
- Plexer als Multi-Konsumenten-Router (Heimgeist, semantAH, Logging)
- Metriken auf Plexer (Eventrate, Fehlerrate, Latenz)

Damit wird Plexer zum Nervengeflecht des Heimgewebe-Organismus.
