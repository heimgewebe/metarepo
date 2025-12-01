# Architecture Decision Records (ADRs)
Kurzer Index der akzeptierten Entscheidungen:

- [ADR-0001: Contracts v1 & JSONL append-only](./0001-contracts-v1-jsonl.md) — Accepted (2025-10-12)
- [ADR-0002: Fleet-Rollout via reusable GitHub Actions](./0002-reusable-actions-rollout.md) — Accepted (2025-10-12)
- [ADR-0006: Umbenennung von `leitstand` zu `chronik` und Einführung eines UI-Repos](./006-rename-leitstand-to-chronik.md) — Accepted (2025-11-14)
- [ADR-0021: Scope & Boundaries of Plexer in the Heimgewebe Organism](./0021-plexer-scope-and-boundaries.md) — Accepted (2025-12-01)

## Weitere ADRs & Ressourcen
- [ADR-Governance & Format](./000-adr-governance.md)
- [WGX (Engine) vs. metarepo (Tower)](./001-engine-vs-tower.md)
- [Fleet-Distribution & Drift-Regeln](./002-distribution-drift.md)
- [CI-Reusables & Pinning-Policy](./003-ci-reusables-pinning.md)
- [.wgx/profile.yml v1 – Minimal-Schema](./004-wgx-profile-v1.md)
- [Evidence-Packs & Link-Health](./005-evidence-linkhealth.md)
- [ADR-Template](./000-template.md)

## CI-Linting für ADRs

Die ADR-Dateien werden automatisiert in CI geprüft:

- Dateinamen: `docs/adrs/NNN-title.md` oder `docs/adrs/NNNN-title.md` mit führenden Nullen.
- Erste Zeile: `# ADR-<NUM> <Title>`; die Nummer im Header muss mit der Nummer im Dateinamen übereinstimmen.
- Metadaten:
  - `Datum: YYYY-MM-DD`
  - `Status: Proposed | Accepted | Superseded` (weitere Status sind erlaubt, erzeugen aktuell aber nur Warnungen).
- Stale-Check: ADRs mit `Status: Proposed`, deren `Datum` mehr als 7 Tage zurückliegt, werden in CI als „bitte entscheiden“ markiert (Warning).

Lokal kannst du dieselben Prüfungen ausführen mit:

```bash
just adr-lint
```
