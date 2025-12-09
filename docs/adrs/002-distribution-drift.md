# ADR-002 Fleet-Distribution & Drift-Regeln
![status: proposed](https://img.shields.io/badge/status-proposed-yellow)
Datum: 2025-10-05
Status: Proposed
Owner: fleet-team
## Kontext
Templates unter `templates/**` werden in Sub-Repos gespiegelt.
## Entscheidung
- Pull-Lernen bevorzugen; nur bei Konflikt Push-Kanon.
- Drift-Reports unter `reports/` je Lauf; PR-Notizen verpflichtend.
## Konsequenzen
Kuratierte Verbesserungen, weniger heimliche Abweichungen.
## Alternativen
Hartes Überschreiben (verliert lokale Verbesserungen).
## Links
- docs/templates.md, docs/fleet/fleet.md
