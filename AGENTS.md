# AGENTS.md — Codex Leitfaden (Metarepo ↔ Sub-Repos)

## Ziel
Metarepo dient als zentraler, lernender Meta-Layer. Es spiegelt **kanonische Templates** (Workflows, Justfile, Docs, WGX-Profile) in Sub-Repos und **zieht Verbesserungen** aus Sub-Repos zurück (dialektisches Lernen).

## Repos
- GitHub Organisation: `heimgewebe`
- Alle Repos öffentlich, außer `vault-privat`.
- Primäre Kinder: `weltgewebe`, `hausKI`, `hauski-audio`, `semantAH`, `wgx`, `metarepo`, `chronik`, `aussensensor`, `heimlern`, `tools`

## Rollen
- **Metarepo**: Quelle der Wahrheit für Templates unter `templates/**`.
- **Sub-Repo**: Darf Templates verbessern → Codex extrahiert Delta, prüft, kuratiert, hebelt ins Metarepo hoch.

## Policies
- Keine Geheimnisse/Secrets in Templates.
- Einheitliche Pfade:
  - Workflows: `.github/workflows/*.yml`
  - WGX-Profil: `.wgx/profile.yml`
  - Docs: `docs/**`, inkl. `docs/wgx-konzept.md`, ADR Template `docs/adrs/0000-template.md`
  - Justfile: `Justfile`
- Änderungen laufen über PRs mit **Reconciliation Report**.
- Commit-Konvention (empfohlen):
  - `chore(templates): sync from <repo>@<sha>: <pattern>`
  - `feat(templates): adopt upgraded ADR template from <repo>@<sha>`

## Haupt-Tasks
1) **Pull-Lernen**: Ausgewählte Patterns aus Sub-Repo nach `metarepo/templates/**` ziehen.
2) **Drift-Check**: Unterschiede zwischen Metarepo-Template und Ziel-Repo prüfen.
3) **Reconcile**: Gewinnerregeln anwenden (Kanonik schlägt lokal, außer „im Feld“ verbesserte Qualität → kuratieren → Kanon updaten).
4) **Push/PR**: Aktualisierte Templates in Sub-Repos spiegeln.

## Tooling
- `scripts/sync-templates.sh` — bidirektional (pull/push), Filter über `--pattern`.
- `scripts/wgx-doctor` — Drift-Meter + Reconciliation Report (Markdown unter `reports/`).
- **Owner-Parameter**: `GITHUB_OWNER` oder `--owner` setzen, z. B. `export GITHUB_OWNER=org && ./scripts/wgx-doctor --repo X --owner-from-env` bzw. `./scripts/sync-templates.sh --push-to X --owner org`.

## Sicherheitsmodus
- Kein Commit ohne Diff-Vorschau.
- NV: Red-Flag, wenn Datei „funktional“ (z. B. produktiver Code) und nicht im Template-Set → nie überschreiben.

## Standard-Befehle
- Pull Lernen: `./scripts/sync-templates.sh --pull-from <repo> --pattern "<glob>"`
- Push Kanon: `./scripts/sync-templates.sh --push-to <repo> --pattern "<glob>"`
- Drift Report: `./scripts/wgx-doctor --repo <repo> --patterns "<glob1>,<glob2>"`

## WGX
- WGX ist dünner Meta-Layer; Standardkommandos: `wgx up|list|run|doctor|validate|smoke`.
- `.wgx/profile.yml` spiegelt Service-Topologie, Envs-Prio: Devcontainer → Devbox → mise/direnv → Termux.
