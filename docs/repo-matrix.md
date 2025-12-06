# Repo-Matrix

Diese Matrix zeigt die **Core-Fleet** des Heimgewebes.
Weitere Repos („related“ und „private“) sind in `overview.md` beschrieben.

**Wichtig:**
Dies ist **nicht die gesamte Organisation**, sondern nur die operative Fleet.

| Repo              | Rolle                               | Fleet |
|-------------------|-------------------------------------|--------|
| metarepo          | Control-Plane, Templates, Contracts | yes    |
| wgx               | Fleet-CLI / Motorik                  | yes    |
| contracts         | Schema-Definitionen für Events/Tools | yes    |
| hausKI            | KI-Orchestrator (Rust)               | yes    |
| hausKI-audio      | Audio-Schicht                        | yes    |
| heimlern          | Lern-/Policy-Schicht                 | yes    |
| semantAH          | Embeddings / Wissensschicht          | yes    |
| aussensensor      | Außenwelt-Events                     | yes    |
| chronik           | Persistenz/Audit                     | yes    |
| tools             | Skripte & Hilfsprogramme             | yes    |
| mitschreiber      | Dialog-/Schreibschicht               | yes    |
| sichter           | Review-Agent / Semantic Checks       | yes    |
| leitstand         | Dashboard / UI                       | yes    |
| heimgeist         | Meta-Agent / Beobachtung             | yes    |
| plexer            | Agent-Routing / Orchestrierung       | yes    |


## Related (nicht Fleet)

| Repo              | Rolle                      | Fleet  |
|-------------------|----------------------------|--------|
| weltgewebe        | Web/Doku/Externe Signale   | no     |

Weitere Details zu Related-Repos: siehe `overview.md`.

## Private
| vault-gewebe      | Privater Obsidian-Vault (nie Fleet) | no |
