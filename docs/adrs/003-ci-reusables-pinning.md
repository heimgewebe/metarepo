# ADR-003 CI-Reusables & Pinning-Policy
![status: proposed](https://img.shields.io/badge/status-proposed-yellow)
Datum: 2025-10-05
Status: Proposed
Owner: ci-team
## Kontext
Sub-Repos referenzieren metarepo-Workflows.
## Entscheidung
- Referenzierung mit Tag oder Commit-SHA (kein floating außer bewusst `@main`).
- Funktionale Engine-Checks liegen in WGX; Tower-Workflows rufen WGX auf.
## Konsequenzen
Reproduzierbare Pipelines, klare Verantwortlichkeit.
## Alternativen
Inline-Workflows in jedem Repo (Pflegeaufwand).
## Links
- docs/ci-reusables.md
