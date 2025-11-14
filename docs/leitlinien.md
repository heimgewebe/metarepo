# Leitlinien · Heimgewebe

## Daten & Formate
- JSONL ist **append-only**: jede Zeile genau ein JSON-Objekt, UTF-8.
- Producer validieren gegen Schemas in `metarepo/contracts/*.schema.json`.
- Editierbare Wahrheit: Dateien (Vault, Code) + Git.
- Abgeleitetes (Indizes/Insights) ist rebuildbar.
- Gerätestate (SQLite) wird **nicht** zwischen Geräten gesynct; stattdessen Events replizieren.

## Events & Schemas (Contracts v1)
- aussensensor/weltgewebe → `aussen.event.schema.json`
- semantAH → `insights.schema.json`
- wgx → `metrics.snapshot.schema.json`
- hausKI JSONL Event-Log → `event.line.schema.json`
- heimlern Decisions → `policy.decision.schema.json`

## Security
- Ingest lokal; optional Shared-Secret via Header `x-auth`.
- Keine Secrets ins Repo; Tokens nur lokal/als CI-Secret.

## Ports & Endpunkte
- chronik: `POST /ingest/{domain}` → `data/{domain}.jsonl`
- Domains: `aussen`, `pc`, `musik`, `heute`, …

## CI
- Schema-Checks via reusable Workflow `contracts-validate` (AJV).
- Kleine Beispielartefakte in PRs validieren lassen.

## Contracts-First

## Mantras
- Dateien & Code syncen, **State nie**.
- **Events immer** (append-only, deterministisch mergen).
- Explainability: Entscheidungen tragen ein `why`.
