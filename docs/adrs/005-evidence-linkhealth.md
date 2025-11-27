# ADR-005 Evidence-Packs (light) & zentraler Link-Health
![status: proposed](https://img.shields.io/badge/status-proposed-yellow)
Datum: 2025-10-05
Status: Proposed
Owner: ci-team
## Entscheidung
- Evidence-Packs bündeln guard/smoke-Summaries + tool-versions (timecapsule-light).
- Link-Check (lychee) läuft zentral im metarepo (Nightly), nicht in allen Repos.
## Konsequenzen
Nachvollziehbare PRs, weniger Lint-Lärm in Sub-Repos.
## Links
- docs/ci-reusables.md
