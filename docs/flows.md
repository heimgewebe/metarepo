# Event-Flüsse: Außen → Leitstand → Policies

## Aktueller MVP-Pfad (bewusst doppelt)
1. `aussensensor` erzeugt kuratierte Außen-Events (`export/feed.jsonl` · `aussen.event.schema.json`).
2. Push **an `leitstand`** (*Bevorzugt*): `POST /ingest/aussen` (oder `/v1/ingest` sobald verfügbar).
3. Parallel (MVP): **direkter Push an `heimlern`** zur frühen Policy-Evaluation.

→ Dieser Doppelpfad ist **temporär** und dient der iterativen Entwicklung von Policies.

## Zielarchitektur (Single Ingest)
1. `aussensensor → leitstand` (einziger Ingest).
2. `heimlern` konsumiert Ereignisse **von `leitstand`** (z. B. Stream/Webhook/Batch).
3. `hausKI` fragt `heimlern` (`/v1/policy/decide`) und liefert Feedback (`/v1/policy/feedback`).

### Migrationsnotizen
- `aussensensor`: `push_heimlern.sh` im Header als **MVP-Pfad** markieren; `push_leitstand.sh` als Preferred.
- `leitstand`: OpenAPI-Spec für `POST /v1/ingest` bereitstellen (Domains intern geroutet).
- `heimlern`: Ingest von `leitstand` (Polling/Stream) vorbereiten.

Siehe auch: [`docs/architecture.md`](./architecture.md), [`docs/overview.md`](./overview.md).