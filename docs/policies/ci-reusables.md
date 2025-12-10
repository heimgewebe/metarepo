# CI-Reusables aus dem metarepo

Das metarepo stellt wiederverwendbare GitHub-Actions-Workflows bereit,
die Sub-Repos direkt referenzieren. Sie bilden die Fleet-Standards ab und
verweisen bei Bedarf auf die WGX-Engine im [WGX-Repository](https://github.com/heimgewebe/wgx).

## Verfügbare Workflows

* `wgx-guard.yml` – überprüft das Vorhandensein des WGX-Profils (`.wgx/profile.yml`).
* `wgx-smoke.yml` – ruft den `reusable-ci`-Workflow mit Standard-Inputs auf (Lint ja, Tests nein).
* `reusable-ci.yml` – generischer CI-Baustein mit optionalen Lint- und Test-Schritten (`just`).
* **Zentraler Reusable:** `.github/workflows/reusable-validate-jsonl.yml` (liegt im metarepo) validiert JSONL-Zeilen gegen Contracts (AJV Draft 2020-12). Consumer-Repos referenzieren ihn via `uses: heimgewebe/metarepo/...`.

  * **Aktuelle Nutzung (Stand jetzt):** `aussensensor`, `chronik`, `heimlern`.
    `hausKI` bindet ihn nur, wenn dort JSONL-Feeds/Fixtures geprüft werden sollen.

## Konsum in Sub-Repos

```yaml
# .github/workflows/wgx-guard.yml im Ziel-Repo
name: WGX Guard
on:
  push:
    branches: [main]
  pull_request:

jobs:
  guard:
    uses: heimgewebe/metarepo/.github/workflows/wgx-guard.yml@main
```

Zusätzliche Beispiel-Einbindung für den Smoke-Workflow:

```yaml
jobs:
  smoke:
    uses: heimgewebe/metarepo/.github/workflows/wgx-smoke.yml@main
    with:
      run_tests: true
```

* JSONL-Validierung (z. B. für `aussensensor`):

```yaml
jobs:
  validate:
    uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
    with:
      jsonl_path: export/feed.jsonl
      schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/aussen.event.schema.json
      strict: false
      validate_formats: true
```

### Zusätzliche Inputs (JSONL-Reusable)

* `schema_path`: Liest das Schema direkt aus dem Repo (überschreibt `schema_url`).

* `validate_formats`: Steuert Formatprüfungen durch `ajv` (Default `true`).

* `jsonl_paths_list`: Komma- **oder** zeilengetrennte Liste von JSONL-Dateien (**Globs erlaubt**). Wenn gesetzt, wird **jede** Datei validiert (rückwärtskompatibel zu `jsonl_path`).
  → Deduplizierung ist aktiviert, leere Globs erzeugen Notices.

* `fail_on_empty`: Wenn `true`, schlägt der Job fehl, sobald kein Treffer (weder Einzelpfad noch Globs) gefunden wird (Default `false`).

* Artefakte mit fehlgeschlagenen Zeilen bleiben sieben Tage verfügbar.

* Verwende immer einen **festen Ref** (`heimgewebe/metarepo@<tag|sha>`). Für reproduzierbare Builds **Tag oder Commit-SHA** pinnen (Actions innerhalb des Workflows sind per SHA fixiert).

  * Beispiel Tag: `@metarepo-ci-v20251005`
  * Beispiel Commit: `@d34db33f5e7c0de...`

* `reusable-ci.yml` akzeptiert `run_lint`/`run_tests` (Booleans). Weitere Inputs bei Bedarf ergänzen.

* JSONL-Workflow: `strict: true` aktiviert den strikten AJV-Modus, `strict: false` erlaubt entspanntere Eingaben. Standard ist `false`.

## Beispiele

**Einzeldatei**

```yaml
jobs:
  validate:
    uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
    with:
      jsonl_path: export/feed.jsonl
      schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/aussen.event.schema.json
```

**Mehrere Dateien (Liste + Globs)**

```yaml
jobs:
  validate:
    uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
    with:
      jsonl_paths_list: |
        export/feeds/*.jsonl
        fixtures/aussen/demo.jsonl
      schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/aussen.event.schema.json
      fail_on_empty: true
```

### Hinweise zum Verhalten

* **Globs** werden per `compgen -G` expandiert; Treffer werden **dedupliziert**.
* **Leere Treffer** führen standardmäßig **nicht** zum Fehler (Notice). Mit `fail_on_empty: true` kannst du das Verhalten schärfen.
* **Fehler-Aggregation:** Alle Dateien/Zeilen werden geprüft; alle Schema-Verstöße werden gesammelt (`::error`) und zusätzlich als Artefakt (`jsonl-violations`) hochgeladen. Der Job schlägt **am Ende** fehl, wenn mindestens ein Verstoß vorhanden war.
* **Abschluss-Logging:** Für jede geprüfte Datei wird die Zeilenzahl als `::notice` ausgegeben.

## Versionierung & Pinning

* `main` spiegelt den aktuellen Fleet-Kanon.
* Für reproduzierbare Pipelines Tags nutzen (`git tag metarepo-ci-vYYYYMMDD`), dann `@metarepo-ci-vYYYYMMDD` referenzieren.
* Funktionale Änderungen (z. B. echte WGX-Checks) entstehen im WGX-Repo und werden hier nur verlinkt.

## Caching-Hinweise

* Lint/Test-Schritte basieren auf `just`. Stelle sicher, dass das Ziel-Repo entsprechende Rezepte anbietet.
* Weitere Tools (z. B. `wgx`, `uv`, `lychee`) werden bei Bedarf projektindividuell installiert; dokumentiere Anpassungen im PR.

---
