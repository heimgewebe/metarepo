# Heimgeist Contracts & Events

## Canonical Source of Truth (SSOT)

Canonical source of truth for Heimgeist Insight Events lives here (`metarepo/contracts/events/heimgeist.insight.v1.schema.json`).
All other repos must mirror or validate against this schema.

It inherits from the **Base Event Envelope** (`base.event.schema.json`).

The definitive structure for `heimgeist.insight` (v1) events is:

```json
// Wrapper-Struktur
{
  "kind": "heimgeist.insight",
  "version": 1,
  "id": "evt-${insight.id}", // z.B. evt-uuid...
  "meta": {
    "occurred_at": "ISO8601-Timestamp",
    "producer": "archivist" // Persistierer (ehemals role)
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
- **meta.producer**: Die technische Rolle, die das Event persistiert hat (z. B. `archivist`, `heimgeist`, `wgx`).
- **data.origin.role**: Die logische Rolle, die die Erkenntnis generiert hat, falls abweichend.

### Transport
- **Methode:** `POST /ingest/heimgeist`
- **Header:** `X-Auth: <token>`
