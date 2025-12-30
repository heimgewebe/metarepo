# Umgebung & Secrets

Diese Seite beschreibt, wie lokale Umgebungen für Heimgewebe-/Metarepo-Aufgaben vorbereitet werden
und welche Variablen bzw. Secrets benötigt werden.

## Basisanforderungen

- **`just`** – wird in [README.md](../README.md) vorausgesetzt (Paketmanager oder `cargo install just`).
- **`yq`** – das Metarepo lädt die passende Version automatisch; eine systemweite Installation ist
  optional.
- **GitHub CLI (`gh`)** – hilfreich für Authentisierung & Repo-Verwaltung.

Weitere Tools (z. B. `wgx`, `uv`) werden in den jeweiligen Repos erklärt.

## Wichtige Umgebungsvariablen

| Variable | Zweck | Wo genutzt |
| --- | --- | --- |
| `AUSSENSENSOR_DIR` | Pfad zum `aussensensor`-Repo für End-to-End-Läufe | [`scripts/e2e/run_aussen_to_heimlern.sh`](../../scripts/e2e/run_aussen_to_heimlern.sh) |
| `CHRONIK_INGEST_URL` | HTTP-Endpunkt des Chronik-Ingests | [`scripts/e2e/run_aussen_to_heimlern.sh`](../../scripts/e2e/run_aussen_to_heimlern.sh) |
| `CHRONIK_TOKEN` | Authentisierungstoken für Chronik-Ingest | [`scripts/e2e/run_aussen_to_heimlern.sh`](../../scripts/e2e/run_aussen_to_heimlern.sh) |
| `HEIMLERN_INGEST_URL` | HTTP-Endpunkt für Policy-Feedback | [`scripts/e2e/run_aussen_to_heimlern.sh`](../../scripts/e2e/run_aussen_to_heimlern.sh) |
| `GH_TOKEN` | GitHub-PAT für `wgx`/CI sowie HTTPS-Clones | [`scripts/wgx`](../../scripts/wgx) |
| `GITHUB_OWNER` / `WGX_OWNER` | Überschreibt den Owner für `wgx`-Kommandos | [`scripts/wgx`](../../scripts/wgx) |

Weitere Variablen entnimmst du den Sub-Repo-Dokumentationen (siehe
[Systemübersicht](../archive/system-overview.md)).

## Umgang mit Secrets

1. **Nicht in Git committen** – nutze `.env` oder deinen Passwortmanager.
2. **Lokale `.env`-Datei** – lege z. B. `.env.local` an und exportiere Variablen via
   `source .env.local`, bevor du Skripte aufrufst. Viele Tools respektieren `dotenv`-Konventionen.
3. **CI-Secret-Management** – GitHub Actions: Secrets auf Orga-/Repo-Ebene setzen (`Settings → Secrets`).
4. **Rotationen dokumentieren** – Änderungen an Tokens in [`reports/sync-logs/`](../../reports/sync-logs)
   oder im entsprechenden Runbook festhalten.

## Troubleshooting

- Fehlende Variablen führen zu Abbrüchen mit hilfreichen Fehlermeldungen (z. B. im
  [E2E-Skript](../../scripts/e2e/run_aussen_to_heimlern.sh)).
- `wgx` meldet fehlende Authentisierung, wenn `GH_TOKEN` nicht gesetzt ist.
- Bei mehreren Accounts empfiehlt sich ein dediziertes `.env` pro Umgebung.

## Weiterführende Links

- E2E-Dokumentation (siehe `scripts/e2e/`)
- Weitere Use-Cases und Troubleshooting-Hinweise in Vorbereitung

## Leitstand Runtime/Build Configuration

Diese Variablen steuern das Verhalten des Leitstands (Artefakte, Strictness, Events).

| Variable | Zweck | Status |
| --- | --- | --- |
| `OBSERVATORY_URL` | Basis-URL zum Laden des Observatory-Snapshots | Required |
| `OBSERVATORY_ARTIFACT_PATH` | Pfad zum JSON-Artefakt relativ zur URL | Required |
| `OBSERVATORY_STRICT` | `1` erzwingt Abbruch bei fehlenden Artefakten (kein Fallback) | Empfohlen (Prod) |
| `NODE_ENV` | `production` aktiviert Optimierungen und Strict-Defaults | Required (Prod) |
| `INSIGHTS_DAILY_URL` | Basis-URL für Daily Insights | Optional |
| `INSIGHTS_DAILY_ARTIFACT_PATH` | Pfad zum Insights-JSON | Optional |
| `LEITSTAND_EVENTS_TOKEN` | Secret Token für den Events-Ingest-Endpunkt | Required (Prod) |
| `LEITSTAND_STRICT` | `1` schaltet Leitstand in den Fail-Loud Modus | Empfohlen |
| `OBSERVATORY_OUT_PATH` | Veralteter Alias für Artifact-Path | **Deprecated** (Vermeiden) |
