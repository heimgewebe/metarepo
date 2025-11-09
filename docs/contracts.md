# Contracts v1 – Kurzreferenz

Die Contracts definieren den gemeinsamen Korridor für alle Fleet-Repos. Jede Producer-Anwendung erzeugt Artefakte, die zu einem der Schemas passen, während Consumer und Control-Plane Workflows dieselben Schemas zur Validierung heranziehen.

## Übersicht

| Schema | Producer | Consumer / Zweck |
| --- | --- | --- |
| `contracts/insights.schema.json` | `semantAH` exportiert `vault/.gewebe/insights/today.json` | `leitstand` zeigt Tageswissen, `hausKI` nutzt Fragen für Lern-Jobs |
| `contracts/metrics.snapshot.schema.json` | `wgx metrics snapshot` CLI | `hausKI` ingestet Systemzustand, Reusable CI prüft JSON Dumps |
| `contracts/audio.events.schema.json` | `hausKI-audio` Event-Stream | `leitstand` Panels „Musik/PC“, `hausKI` zum Kontextlernen |
| `contracts/aussen.event.schema.json` | `aussensensor`, `weltgewebe` | `leitstand` Panel „Außen“, Downstream Exports |
| `contracts/event.line.schema.json` | `hausKI` JSONL Event-Log | Fleet-Debugging, Replays, Append-only Sync |
| `contracts/policy.decision.schema.json` | `heimlern` Policies | `hausKI` erklärt Entscheidungen („Warum“), `leitstand` zeigt Begründungen |
| `contracts/os.context.intent.schema.json` | `mitschreiber` | `semantAH` (Graph / Kontextaufbau), `hausKI` (Plan/Execute), `leitstand` (Audit) |

### `contracts/os.context.intent.schema.json`

- **Zweck:** Intent-Ereignisse aus dem lokalen Kontext (User/Editor/System) als JSONL (eine Zeile = ein Objekt).
- **Pflichtfelder:** `actor`, `goal`.
- **Empfohlen:** `ts` (ISO-8601), `scope.repo` oder `scope.path`, `tags[]`.
- **Kontext:** `context.*` bündelt OS/App/Editor-Infos, optional `text.lang`/`text.content` (begrenzte Länge) und `embeddings`.
- **Erweiterbarkeit:** `constraints` und `meta` erlauben lockeres Andocken neuer Hinweise/Transport-Infos.

**CI-Validierung (Beispiel, in Producer-Repos wie `mitschreiber`):**
```yaml
name: validate-intent
on:
  push:
    paths: ["export/**", ".github/workflows/**"]
  pull_request:
jobs:
  ajv:
    uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
    with:
      jsonl_path: export/os.intent.jsonl
      schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/os.context.intent.schema.json
      strict: false
      validate_formats: true
```

## Neue Contracts (IDEal v0.2)

| Schema | Producer | Consumer / Zweck |
| --- | --- | --- |
| `contracts/dev.tooling.schema.json` | Repos mit IDE/Dev-Setup (Templates) | CI-Gate für konsistente Dev-Konfiguration in Fleet-Repos |
| `contracts/knowledge.graph.schema.json` | `wgx knowledge extract`, Parser in `scripts/knowledge/*` | `semantAH` Ingest (Graph), `leitstand` Panel „Wissen“ |
| `contracts/agent.workflow.schema.json` | Agent-/Workflow-Manifeste (YAML → JSON) | `wgx agent validate/run`, `hausKI` Playbooks, Policy-Checks (`heimlern`) |

### Quickstart

**Knowledge-Graph validieren (JSON):**
```yaml
jobs:
  validate-knowledge-graph:
    uses: heimgewebe/metarepo/.github/workflows/validate-knowledge-graph.yml@contracts-v1
    with:
      files_glob: |
        knowledge.graph.json
        docs/**/knowledge.graph.json
```

**Agent-Workflow validieren (YAML→JSON):**
```yaml
jobs:
  validate-agent-workflows:
    uses: heimgewebe/metarepo/.github/workflows/validate-agent-workflow.yml@contracts-v1
    with:
      files_glob: .agent/**/*.yaml
```

### `contracts/aussen.event.schema.json`

- **Pflichtfelder:** `type`, `source`; `url` ist Pflicht, wenn `type = "link"`.
- **Qualität:** `title` und `source` verlangen mindestens ein Zeichen; Tags dürfen keine führenden Leerzeichen enthalten und sind auf 64 Elemente begrenzt.
- **Metafelder:** `features` und `meta` erlauben beliebige Schlüssel zur Anreicherung (Scoring, Parser-Versionen usw.).
- **Zeit & Referenzen:** `ts` nutzt ISO-8601 (`date-time`), `url` prüft URI-Format.
- **ID (optional):** Stabiler Hash (z. B. `sha256(url+ts)`) zur Deduplication.

## Validierung

* JSONL-Feeds (z. B. `aussensensor/export/feed.jsonl`) validierst du mit dem Workflow `.github/workflows/reusable-validate-jsonl.yml`:
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
  - Optional kannst du `schema_path` setzen, um das Schema lokal aus dem Repo zu lesen (Offline-Fall).
  - `validate_formats` steuert Formatprüfungen (`uri`, `date-time`, ...); Standard ist `true`.
  - Der Workflow prüft jede Zeile einzeln mit `ajv` (Draft 2020-12), entfernt CRLF, meldet Schema-Verstöße mit Zeilennummer, pinnt genutzte Actions per SHA und hängt die fehlerhaften Zeilen für sieben Tage als Artefakt an.
  - `strict: true` aktiviert AJV-Strict-Mode; Standard ist `false`, damit Legacy-Felder tolerant eingelesen werden können.
* Für `wgx` existiert zusätzlich `wgx-metrics`, das neben der Schema-Prüfung optional einen POST an das Fleet-Ingest ausführt.

## Pflichten für Producer

1. **JSON-Konformität**: Artefakte müssen valide UTF-8 JSON/JSONL sein.
2. **Append-Only Events**: Event-Logs (`event.line.schema.json`) werden angefügt, nicht überschrieben.
3. **Schema-Versionierung**: Änderungen erfolgen über neue Tags (`contracts-vN`). Consumers pinnen auf den Tag.

## Pflichten für Consumer

1. **Validieren vor Persistenz**: Eingehende Artefakte werden gegen das passende Schema geprüft.
2. **Explainability**: Empfehlungen zeigen `why` aus `policy.decision.schema.json` an (z. B. Leitstand Panel „Warum“).
3. **Metrics Visibility**: `metrics.enable: true` Repos melden Snapshots und konsumieren sie in Dashboards.

## Rollout-Checkliste

1. Branch `chore/fleet-contracts-v1` im Metarepo → Schemas, Workflows, Doku, Template.
2. Tag `contracts-v1` nach Merge.
3. `just fleet open-prs contracts-v1` öffnet Folge-PRs (`feat/contracts-v1`) in allen Repos.
4. Producer (`wgx`, `semantAH`) zuerst mergen, danach Consumer (`hausKI`, `leitstand`) und Policies (`heimlern`).
5. Labels `contracts-v1` & `fleet` im Ziel-Repo anlegen (für Issue-Template `rollout`).

## Weiteres

* Heimlern-Policies sind feature-flagged (`policy.enable=false` = Shadow Mode).
* Rollbacks über Tag `contracts-v1-hotfix` + Migration-Downs in hausKI.
* Alle lokalen Endpunkte laufen auf `localhost` und senden nur opt-in Outbound Requests.

## Versionierung

### contracts-v1 (Tag-Vorbereitung)
- **Schemas**: `contracts/*.schema.json` eingefroren für Producer (`semantAH`, `wgx`, `hausKI-audio`, `aussensensor`) und Consumer (`hausKI`, `leitstand`, `heimlern`).
- **Reusable Workflows**: `.github/workflows/reusable-validate-jsonl.yml` für JSONL-Feeds (`uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1`) und ergänzend `.github/workflows/wgx-metrics.yml` für Snapshot-Checks.
- **Dokumentation**: Übersicht & Datenflüsse in [`docs/overview.md`](./overview.md) sowie Detailbeschreibung im [Gesamtsystem](./heimgewebe-gesamt.md); Release-Ankündigungen erfolgen über diesen Abschnitt.
- **Visuals**: Obsidian Canvas (`docs/canvas/*.canvas`) spiegeln Architektur & Event-Flüsse als Ergänzung zu den Schemas.
