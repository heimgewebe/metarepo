# Heimgewebe Mention Protocol

Dieser Leitfaden beschreibt die kanonische Variante des Heimgewebe-Dispatch-Workflows
(`.github/workflows/heimgewebe-command-dispatch.yml`) und erklärt, wie Pull-Request-Kommentare
mit `@heimgewebe/<zielrepo> /<kommando> [args]` zu Repository-Dispatch-Events werden.

## Zweck
- Zentrale Definition des Mention-Patterns im Metarepo.
- Gehärtete Verarbeitung und Weiterleitung an die Ziel-Repos der Organisation.
- Klare Fehlermeldungen für Tippfehler oder nicht erlaubte Befehle.

## Trigger & Berechtigungen
- Ausgelöst auf `issue_comment` → `created`.
- Wirkt nur auf PRs, die einen `@heimgewebe/…`-Tag enthalten.
- Akzeptiert nur Kommentare von `OWNER`, `MEMBER` oder `COLLABORATOR`.
- Minimal notwendige Rechte: `contents: read`, `issues: write`, `pull-requests: write`
  (für Feedback-Kommentare bei ungültigen Befehlen).

## Befehlssyntax
```
@heimgewebe/<target_repo> /<command> [argumente]
```
- `target_repo`: Whitelist in `ALLOWED_TARGET_REPOS` (Standard: `sichter,wgx,heimgeist,metarepo,hausKI,semantAH,heimlern,chronik,leitstand,tools`).
- `command`: Whitelist in `ALLOWED_COMMANDS` (Standard: `quick,deep`).
- Argumente werden auf 256 Zeichen gekürzt, um Missbrauch zu begrenzen.

## Sicherheitsmaßnahmen
- Kommentartext wird ausschließlich über eine Umgebungsvariable gelesen (CodeQL-sicher).
- Whitelists für Ziel-Repos und erlaubte Kommandos.
- Sanitizing/Kürzung langer Argumente.
- Feedback bei ungültigem Pattern, unbekanntem Repo oder nicht erlaubtem Kommando.

## Payload
Bei erfolgreichem Match wird folgender Payload als JSON an das Ziel-Repo gesendet:
```json
{
  "version": 1,
  "source_repository": "<owner>/<repo>",
  "source_issue_number": <pr-nummer>,
  "source_comment_author": "<login>",
  "raw_comment": "<voller kommentar>",
  "target_repo": "<zielrepo>",
  "command": "<kommando>",
  "args": "<gekürzte argumente>"
}
```
Die Daten werden als Step-Output transportiert; es wird keine temporäre Datei angelegt.

## Secrets
- Erforderlich: `HEIMGEWEBE_AUTOBOT_TOKEN` mit Berechtigungen für `repository_dispatch` in den Ziel-Repos.
- Für Feedback-Kommentare wird das Standard-`GITHUB_TOKEN` genutzt.

## Rollout-Hinweise
- Diese Datei gilt als kanonische Quelle im Metarepo.
- Beim Ausrollen in Sub-Repos sollte der Workflow-Header einen Hinweis enthalten, dass er aus dem Metarepo synchronisiert wird.
