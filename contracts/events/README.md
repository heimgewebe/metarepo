# Heimgeist Contracts & Events

## Sync-Punkt A: Mini-Spezifikation (v1)

**Source of Truth (SoT):** `metarepo/contracts/events/heimgeist.insight.v1.schema.json`

Dieses Verzeichnis enthält Contracts für die Domain `heimgeist`.
Die gemeinsame Wahrheit für `heimgeist.insight` Events ist wie folgt definiert:

```json
// Wrapper-Struktur
{
  "kind": "heimgeist.insight",
  "version": 1,
  "id": "evt-${insight.id}", // z.B. evt-uuid...
  "meta": {
    "occurred_at": "ISO8601-Timestamp",
    "role": "archivist" // Persistierer
  },
  "data": {
    // Payload (Strict DTO)
    "insight_type": "...",
    "summary": "...",
    "details": "...",
    "origin": { // Optional: Ursprüngliche Quelle
       "role": "heimgeist"
    }
  }
}
```

### Semantik
- **meta.role**: Die technische Rolle, die das Event persistiert hat (z. B. `archivist`).
- **data.origin.role**: Die logische Rolle, die die Erkenntnis generiert hat (z. B. `heimgeist`), falls abweichend.

### Transport
- **Methode:** `POST /ingest/heimgeist`
- **Header:** `X-Auth: <token>`
