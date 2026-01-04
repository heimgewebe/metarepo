# 0031. Contract Ownership & Guard

* Status: Accepted
* Datum: 2026-01-04
* Deciders: Jules, User
* Consulted: Fleet
* Informed: Fleet

## Context

Das Heimgewebe lebt von einer "Single Source of Truth". Das `metarepo` dient als Control-Plane für den Organismus und hostet die kanonischen Definitionen für Fleet (`repos.yml`) und interne Contracts (`contracts/**`).

Ohne technische Durchsetzung entstehen lokal korrekte, aber organismisch driftige PRs, bei denen Contracts in falschen Repos ("Satelliten") definiert werden. Dies führt zu Version-Schisma und erhöhtem Wartungsaufwand (Adapter-Hölle).

Gleichzeitig existiert das `contracts-mirror` Repository, welches spezifisch dazu dient, externe oder abgeleitete Schemas (`json/**`, `proto/**`) zu spiegeln. Es darf jedoch keine eigenen *internen* Organismus-Contracts definieren, die in Konkurrenz zum Metarepo stehen.

## Decision

Wir etablieren einen strikten **Contract-Ownership-Guard**, der folgende Invarianten technisch erzwingt:

1.  **Metarepo-Exklusivität für interne Contracts**:
    *   Änderungen im Verzeichnis `contracts/**` sind **nur** im `metarepo` erlaubt.
    *   In allen anderen Repos (inklusive `contracts-mirror`) ist das Ändern von `contracts/**` verboten.

2.  **Contracts-Mirror Rolle**:
    *   Das `contracts-mirror` Repository darf Änderungen in `json/**`, `proto/**` etc. vornehmen (Spiegelung externer/abgeleiteter Schemas).
    *   Es darf jedoch **nicht** `contracts/**` modifizieren (keine parallele interne Wahrheit).

3.  **Metarepo-Identität**:
    *   Das `metarepo` wird durch das Vorhandensein von `fleet/repos.yml` (und optional `contracts/`) identifiziert.

## Consequences

*   **Positive**:
    *   Verhindert Contract-Drift und "Split-Brain"-Situationen im Organismus.
    *   Erzwingt "Contracts-First" Entwicklung im Metarepo.
    *   Klarheit über die Quelle der Wahrheit.

*   **Negative**:
    *   Erhöht die Hürde für schnelle Fixes in Downstream-Repos (müssen im Metarepo gefixt und gesynct werden).
    *   Erfordert saubere Synchronisations-Pipelines (`scripts/contracts-sync.sh`).

## Compliance

Enforcement erfolgt ausschließlich über den WGX-Guard `contracts_ownership` im Repository `heimgewebe/wgx`. Alle Fleet-Repos müssen `wgx guard` in CI ausführen.
