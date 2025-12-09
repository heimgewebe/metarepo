# Runbooks in der Fleet verteilen

Runbooks sind klickbare Markdown-Anleitungen, die in den Sub-Repos landen sollen.
Sie liegen im metarepo unter `templates/docs/runbooks/` (lege bei Bedarf neue Dateien dort an).

## Lifecycle
1. **Authoring im metarepo** – neue Runbooks als Markdown schreiben.
2. **Sync** – `just up` oder `scripts/sync-templates.sh --pattern "templates/docs/runbooks/*.md"`.
3. **Review** – In der Sync-PR verlinken, wie der Runbook-Eintrag im Ziel-Repo benutzt wird (z. B. README-Abschnitt, Issue-Vorlage).

## Gestaltung
- Dateiname im Format `NNN-name.md` für sortierbare Listen (z. B. `010-oncall-start.md`).
- Erster Absatz: Zweck + Zielgruppe.
- Verwende Callouts (`> ℹ️`) für Hinweise, Checklisten als Checkboxen (`- [ ]`).

## Ausführung über WGX
- WGX kann Runbooks als Task referenzieren (`wgx run runbooks/<name>`), sobald ein entsprechendes Profil existiert.
- Wenn ein Runbook einen Befehl benötigt, pflege den Command in `.wgx/profile.yml` und verlinke ihn aus dem Markdown.

## Ownership
- Jede Runbook-Datei **muss** einen Owner im Frontmatter tragen, z. B.:
  ```yaml
  ---
  title: Oncall Start
  owner: fleet-team
  severity: info
  ---
  ```
- Änderungen immer mit dem Owner abstimmen und im PR erwähnen.

> 💡 Runbooks sind **Stubs**: Sie erklären das „Wie“ für die Fleet.
> Tool-spezifische Details (z. B. WGX-Subcommands) werden in der WGX-Doku gepflegt.
