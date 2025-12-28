# ADR-0028 Leitstand Strict Build Symmetry
Datum: 2025-12-28
Status: Accepted
Owner: heimgewebe/metarepo (Policy), umgesetzt in heimgewebe/leitstand (Build/CI)
Scope: Leitstand Build-Pipeline (Cloudflare Pages / Production), Artefakt-Konsum

## Context

Leitstand visualisiert zwei Wissensschichten:
- **Raw Observatory** (`knowledge.observatory.json`) als Herkunftsraum, prüfbarer Kontext.
- **Published Daily** (`insights.daily.json`) als verdichtete, veröffentlichte Erkenntnis.

Bisher konnte es passieren, dass Production-Builds „grün“ deployen, obwohl eine der Schichten fehlt oder nur via Fixture existiert. Das erzeugt „grüne Wahrheit ohne Daten“ und widerspricht dem Prinzip Truth via CI.

## Decision

In Production-Strictness gilt:

### 1. Strict Symmetry (Raw + Daily oder nichts)
Wenn `LEITSTAND_STRICT=1` (oder `NODE_ENV=production`):

- Beide Artefakte sind zwingend:
    - `artifacts/knowledge.observatory.json`
    - `artifacts/insights.daily.json`
- Fehlt eines, ist leer oder nicht parsebar ⇒ Build muss hart fehlschlagen.

### 2. Single Production Entry-Point
Production-Build ist ausschließlich:

- `pnpm build:cf` (Fetch → Verify → Static Build)

`pnpm build:static` darf in Strict nicht erfolgreich sein.

### 3. Forensic Trace (nicht autoritativ)
`artifacts/_meta.json` wird als Belegspur geführt:

- wann gefetcht wurde
- von welcher Quelle
- Dateigrößen
- Parse-Status
- minimale, optionale Extrakte (z. B. ts bei Daily)

`_meta.json` hat keinerlei Entscheidungsautorität; es ist Debug/Forensik.

## Rationale
- **Epistemische Kopplung:** Published ohne Raw ist eine Behauptung ohne Beleg.
- **Determinismus:** Production darf keine impliziten Nebenpfade haben (Runtime-Fetch, Fixture-Fallback, zufälliges build:static).
- **Drift-Schutz:** Ein Build-Pfad und eine Strict-Variable reduzieren Fehlkonfigurationen.

## Consequences

### Positive
- Keine Deploys mit leeren/halben Wahrheiten.
- Fehler werden früh, laut und eindeutig sichtbar.
- UI kann Herkunft sauber ausweisen.

### Negative
- Mehr rote Builds bei Netzwerkflakiness oder Rate-Limits.
- Höherer Druck, Fetch-Robustheit zu verbessern.

### Mitigation (nicht Teil dieser ADR-Umsetzung)
- Retries/Timeouts/Backoff in Fetch-Skripten.
- Optional: Spiegelung/Caching der Release-Assets.

## Implementation Notes
- `build-static` bleibt reiner Konsument (kein Fetch).
- Server Runtime in Strict: kein Fixture, stattdessen klarer 503 bei Missing/Invalid.
- CI/Deploy-Docs müssen den einzigen Production-Pfad explizit machen.

## Compliance / Guardrails

A change is compliant iff:
- Strict + missing/invalid raw oder daily ⇒ Exit 1.
- Strict + build:static ⇒ Exit 1 mit Hinweis auf `pnpm build:cf`.
- Non-strict darf Fixtures nutzen, muss aber sichtbar markieren (UI + Meta).
