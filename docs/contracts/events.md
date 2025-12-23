# Heimgewebe Event Contracts

## Base Event Envelope (v1)

The canonical definition for all system events is defined in `metarepo/contracts/events/base.event.schema.json`.

**Structure:**
- `kind` (string): Event type designator.
- `version` (integer): Schema version number.
- `id` (string): Unique ID starting with `evt-`.
- `meta` (object): Metadata, requiring `occurred_at` (ISO8601) and `producer` (string).
- `data` (object): Domain-specific payload.

## Legacy Envelopes (Chronik Adapter)

Older event formats (e.g., flat `id`, `ts`, `type`, `payload` structures found in legacy `event.line.schema.json`) are considered **Legacy**.

Chronik will support these via an **Adapter Layer** during the transition period.
New producers MUST use the Base Event Envelope.
Legacy envelopes are NOT alternative standards; they are deprecated formats pending removal.
