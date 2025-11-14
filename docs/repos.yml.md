# `repos.yml` – Inventar & Filter

`repos.yml` definiert, welche Repositories vom metarepo als Teil der Fleet behandelt werden.
Das File wird von `scripts/wgx` und `scripts/sync-templates.sh --repos-from` gelesen.

> **Parser-Verhalten:** Leere Werte wie `key:` oder `-` (ohne nachfolgende Daten) werden von
> `scripts/repo_config.py` als `null` (`None`) interpretiert. Verwende explizite
> Anführungszeichen (`""`), falls ein leerer String benötigt wird.

## Schema
```yaml
# Modus: "static" (nur Liste) oder "github" (per GitHub-API ermitteln)
mode: static

# GitHub-Owner/Organisation der Fleet
github:
  owner: heimgewebe

# Statische Fleet-Liste (genutzt, wenn mode: static)
repos:
  # --- Core (Fleet) ---
  - name: metarepo
    url: https://github.com/heimgewebe/metarepo
    default_branch: main
  - name: hausKI
    url: https://github.com/heimgewebe/hausKI
    default_branch: main
  - name: hausKI-audio
    url: https://github.com/heimgewebe/hausKI-audio
    default_branch: main
    depends_on:
      - hausKI
  - name: heimlern
    url: https://github.com/heimgewebe/heimlern
    default_branch: main
  - name: aussensensor
    url: https://github.com/heimgewebe/aussensensor
    default_branch: main
  # - name: chronik
  #   url: https://github.com/heimgewebe/chronik
  #   default_branch: main
  - name: wgx
    url: https://github.com/heimgewebe/wgx
    default_branch: main
  - name: semantAH
    url: https://github.com/heimgewebe/semantAH
    default_branch: main

static:
  include:
    # --- Verwandt (nicht Fleet) ---
    - name: weltgewebe
      url: https://github.com/heimgewebe/weltgewebe
      default_branch: main
    # vault-gewebe (inkl. privat) ist persönlicher Speicher und gehört nicht zur Fleet
```

> **Hinweis:** Repo-Name: `hausKI` (großes `KI`). Beispiele in Befehlen und Pfaden nutzen **`hausKI`** – Case-sensitive!

### Status-Empfehlung (optional)
Erweitere Einträge bei Bedarf um `status: core|related|personal`. Fleet-Tools können damit filtern:
```yaml
- name: hausKI
  status: core
- name: weltgewebe
  status: related
```

### Felder
- `mode`
  - `static` (Default): Fleet-Liste kommt aus `repos` + `static.include`.
  - `github`: Fleet wird dynamisch über `gh repo list <owner>` bestimmt.
- `github.owner`: GitHub Namespace. Wird auch von `scripts/sync-templates.sh --owner-from-env` genutzt.
- `repos`: Kernmenge der Repositories. Jeder Eintrag besitzt mindestens das Feld `name`, optional `url`, `default_branch` und `depends_on`.
- `static.include`: Ergänzende Repos, z. B. wenn `repos` leer bleiben soll. Aufbau identisch zu `repos`.

## Standard-Policy
- Fleet umfasst alle **öffentlichen** Repos unter `heimgewebe`.
- Ausnahme: `vault-gewebe` bleibt aus Datenschutzgründen ausgeschlossen (liegt weiter bei `alexdermohr`).

## Praxis-Tipps
- Für einmalige Pushes `scripts/sync-templates.sh --repos-from repos.yml --pattern "templates/.github/workflows/*.yml"`.
- Bei `mode: github` regelmäßig `gh auth status` prüfen (Token für `gh repo list`).
- Änderungen an `repos.yml` immer mit PR begründen (z. B. neues Repo aufgenommen / stillgelegt).
