# ADR-001 WGX (Engine) vs. metarepo (Tower)
![status: proposed](https://img.shields.io/badge/status-proposed-yellow)
Datum: 2025-10-05
Status: Proposed
Owner: fleet-team
## Kontext
WGX liefert Bedienkanon, Guard/Smoke, Policies; metarepo verteilt und beobachtet.
## Entscheidung
- WGX-Doku bleibt ausschließlich im WGX-Repo; metarepo liefert nur Stubs/Links.
- Metarepo verteilt Templates/CI-Reusables und ruft WGX auf; keine eigene Guard/Smoke-Logik.
## Konsequenzen
Kein Dokument-Drift, eine Quelle der Wahrheit, klarer Update-Pfad.
## Alternativen
Doppelte Doku/Checks im Tower (führt zu Drift).
## Links
- docs/fleet.md, docs/ci-reusables.md, docs/wgx-stub.md
