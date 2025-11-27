# ADR-0001 Contracts v1 & JSONL append-only
Status: Accepted
Datum: 2025-10-12

## Kontext
Einheitlicher Datenaustausch zwischen Fleet-Repos.

## Entscheidung
- JSONL als append-only Event-Format.
- Schemas in `contracts/*.schema.json`, Validation via reusable CI.

## Konsequenzen
- Deterministische Replikation, einfache Merges.
- Strikte Schema-Versionierung (tags `contracts-vN`).

## Alternativen
- Gemeinsame DB: verworfen (Kopplung, Ops-Aufwand).
- Protobuf/Avro: Overhead für MVP.
