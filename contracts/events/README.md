# Heimgeist Contracts & Events

## Sync-Punkt A: Mini-Spezifikation (v1)

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
    "role": "heimgeist" // oder "archivist"
  },
  "data": {
    // Payload (Typ, Summary, Details...)
  }
}
```

### Transport
- **Methode:** `POST /ingest/heimgeist`
- **Header:** `X-Auth: <token>`
