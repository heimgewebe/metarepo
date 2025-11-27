# ADR-0002 Fleet-Rollout via reusable GitHub Actions
Status: Accepted
Datum: 2025-10-12

## Kontext
Viele Repos sollen einheitliche Checks/Validierungen nutzen.

## Entscheidung
- Reusable Workflows im metarepo; Sub-Repos binden per `uses:`.

## Konsequenzen
- Einheitliche Qualitätstore; schneller Rollout.
- Versionierung der Workflows per Tag.

## Alternativen
- Kopierte YAMLs pro Repo: Driftgefahr.
