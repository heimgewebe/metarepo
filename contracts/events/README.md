# Retained Heimgeist Contract IDs & Events

## Canonical Source of Truth (SSOT)

Canonical schema bytes for the retained `heimgeist.insight` event ID live here (`metarepo/contracts/events/heimgeist.insight.v1.schema.json`).
The former `heimgewebe/heimgeist` repository was physically deleted on 2026-09-18. Keeping the contract ID preserves decoding compatibility; it does not establish a current Heimgeist service or producer.

It inherits from the **Base Event Envelope** (`base.event.schema.json`).

### Governance Metadata

Governance information (producers, consumers) is stored separately in `*.meta.json` files to keep schemas strict-mode compliant:
- **Schema**: `heimgeist.insight.v1.schema.json` (validation logic)
- **Governance**: `heimgeist.insight.v1.meta.json` (producers, consumers, documentation)

This separation ensures that JSON Schema validators in strict mode can process schemas without encountering unknown keywords.

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
       "role": "archivist"
    }
  }
}
```

### Semantik
- **meta.producer**: Die technische Rolle, die das Event persistiert hat (z. B. `archivist`, `wgx`). Der historische Wert `heimgeist` kann in Altbeständen vorkommen, ist aber kein aktueller Service-Claim.
- **data.origin.role**: Die logische Rolle, die die Erkenntnis generiert hat, falls abweichend.

### Transport

Dieser Contract definiert **keinen aktuellen Heimgeist-Endpoint**. Historische Transportpfade des gelöschten Repositories sind nicht als heutige Routing- oder Auth-Anweisung zu verwenden; aktuelle Zustellung ergibt sich aus den jeweils überlebenden Consumer-/Router-Verträgen.
