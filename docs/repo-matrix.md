# Repo-Matrix

Diese Matrix definiert die Struktur des Heimgewebes. Sie ist die **Single Source of Truth** für Fleet-Mitgliedschaft und Rollen.

## Core-Fleet
Diese Repositories bilden den Organismus und unterliegen den Fleet-Policies (CI, WGX-Profil, Contracts).

| Repo              | Rolle                               | Fleet |
|-------------------|-------------------------------------|-------|
| metarepo          | Control-Plane, Templates, Contracts | yes   |
| wgx               | Fleet-CLI / Motorik                 | yes   |
| contracts-mirror  | Schema-Definitionen für Events/Tools| yes   |
| hausKI            | KI-Orchestrator (Rust)              | yes   |
| hausKI-audio      | Audio-Schicht                       | yes   |
| heimlern          | Lern-/Policy-Schicht                | yes   |
| semantAH          | Embeddings / Wissensschicht         | yes   |
| aussensensor      | Außenwelt-Events                    | yes   |
| chronik           | Persistenz/Audit                    | yes   |
| tools             | Skripte & Hilfsprogramme            | yes   |
| mitschreiber      | Dialog-/Schreibschicht              | yes   |
| sichter           | Review-Agent / Semantic Checks      | yes   |
| heimgeist         | Meta-Agent / Beobachtung            | yes   |
| plexer            | Agent-Routing / Orchestrierung      | yes   |
| leitstand         | Observer / UI                       | yes   |
| vault-gewebe      | Privater Obsidian-Vault             | yes   |

## Related / Satellites (Non-Fleet)
Externe Werkzeuge oder Wissensspeicher. Keine Fleet-Policies erforderlich.

| Repo              | Rolle                      | Fleet |
|-------------------|----------------------------|-------|
| weltgewebe        | Web/Doku/Externe Signale   | no    |
| icf-tool          | ICF-Katalog & Browser      | no    |
