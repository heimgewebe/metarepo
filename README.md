# Metarepo – Heimgewebe Control Plane

> **Zentraler Meta-Layer für die Heimgewebe-Fleet**
> Spiegelt kanonische Templates (Workflows, Justfile, Docs, WGX-Profile) in Sub-Repos und zieht Verbesserungen zurück (dialektisches Lernen).

[![CI Status](https://github.com/heimgewebe/metarepo/actions/workflows/ci.yml/badge.svg)](https://github.com/heimgewebe/metarepo/actions/workflows/ci.yml)

## Organismus-Kontext

Dieses Repository ist Teil des **Heimgewebe-Organismus**.

Die übergeordnete Architektur, Achsen, Rollen und Contracts sind zentral beschrieben im
👉 [`metarepo/docs/heimgewebe-organismus.md`](https://github.com/heimgewebe/metarepo/blob/main/docs/heimgewebe-organismus.md)
sowie im Zielbild
👉 [`metarepo/docs/heimgewebe-zielbild.md`](https://github.com/heimgewebe/metarepo/blob/main/docs/heimgewebe-zielbild.md).

Alle Rollen-Definitionen, Datenflüsse und Contract-Zuordnungen dieses Repos
sind dort verankert.

## Überblick

Das **metarepo** ist die Quelle der Wahrheit für:

- **Templates** – Gemeinsame Workflows, Justfiles, Docs und WGX-Profile unter `templates/`
- **Contracts** – JSON-Schemas und OpenAPI-Specs unter `contracts/`
- **Reusable Workflows** – Wiederverwendbare CI-Pipelines unter `.github/workflows/reusable-*.yml`
- **Fleet-Management** – Zentrale Konfiguration aller Heimgewebe-Repos in `repos.yml`

### Heimgewebe-Fleet

Die Fleet umfasst folgende Core-Repos:
- **weltgewebe** – Externe Events und Signale
- **hausKI** – KI-Orchestrator (Rust, GPU, Offline)
- **hauski-audio** – Audio-Pipeline und Telemetrie
- **semantAH** – Wissensextraktion und Embeddings
- **wgx** – Flottenmotor für Sync, Doctor, Metrics
- **chronik** – Event-Ingest und Persistenz
- **aussensensor** – Außen-Signalgeber
- **heimlern** – Lern- und Policy-Engine
- **tools** – Gemeinsame Utilities

## Schnellstart

### Installation

```bash
# 1. Dependencies installieren
just deps          # oder: uv sync --frozen

# 2. Tooling prüfen
just validate      # Linting, Format-Checks, actionlint
```

### Häufige Kommandos

```bash
# Fleet-Übersicht
just list          # WGX-Liste aller Repos

# Templates synchronisieren
just up            # Templates an alle Repos verteilen
just sync          # Manuelle Sync (siehe scripts/sync-templates.sh)

# Validierung
just validate      # Lokale Checks
just smoke         # Schneller Integrationslauf

# Drift-Analyse
scripts/wgx-doctor --repo <repo>  # Drift-Report generieren
```

## Dokumentation

### Kerndokumentation
- [**Architecture**](docs/architecture.md) – Systemübersicht und Schichten
- [**Vision**](docs/vision.md) – Leitlinien und Roadmap
- [**Contracts**](docs/contracts.md) – Schema-Versionierung und Validierung
- [**Fleet Management**](docs/fleet.md) – Template-Sync und Push-Workflows
- [**WGX Konzept**](docs/wgx-konzept.md) – Fleet-Motor und Kommandos
- [**AGENTS.md**](AGENTS.md) – Leitfaden für KI-Agenten

### Entwicklung & Betrieb
- [**Troubleshooting**](docs/troubleshooting.md) – Häufige Probleme und Lösungen
- [**ADRs**](docs/adrs/README.md) – Architecture Decision Records
- [**Runbooks**](docs/runbooks.md) – Betriebsanleitungen
- [**Environment**](docs/environment.md) – Entwicklungsumgebung einrichten

Vollständige Dokumentation: [`docs/`](docs/) · [Vollständiger Index](docs/README.md)

## Entwicklung

### Template-Synchronisation

```bash
# Template aus Sub-Repo lernen (Pull)
./scripts/sync-templates.sh --pull-from weltgewebe --pattern "templates/docs/**"

# Template in Sub-Repo pushen
./scripts/sync-templates.sh --push-to hausKI --pattern "templates/.github/workflows/*.yml"

# Drift-Check durchführen
./scripts/wgx-doctor --repo wgx --patterns "templates/.github/workflows/*.yml,templates/Justfile"
```

### Beitragen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für:
- Setup und Grundprinzipien
- Patch-Flow und Validierung
- Pull Request Guidelines
- Fleet-Push nach Merge

## Projekt-Struktur

```
metarepo/
├── templates/           # Kanonische Templates für Fleet
│   ├── .github/workflows/
│   ├── docs/
│   ├── Justfile
│   └── .wgx/profile.yml
├── contracts/           # JSON-Schemas und OpenAPI-Specs
├── scripts/             # Sync-, Drift- und Fleet-Tools
├── docs/                # Projektdokumentation
├── reports/             # Sync-Logs und Drift-Reports
├── repos.yml            # Fleet-Konfiguration
└── Justfile             # Haupt-Kommandos
```

## Lizenz

Dieses Projekt steht unter der [CC0 1.0 Universal](LICENSE) Public Domain Dedication.

**Hinweis:** Die actionlint-Dokumentation (`LICENSE.txt`, `man/actionlint.1`) stammt vom [actionlint-Projekt](https://github.com/rhysd/actionlint) und ist unter der MIT-Lizenz (siehe `LICENSE.txt`) verfügbar.

## Contributing

Contributions sind willkommen! Bitte lies [CONTRIBUTING.md](CONTRIBUTING.md) für Details zum Entwicklungsprozess.

## MCP / Copilot Integration (heimgewebe-local)

Dieses Repository enthält einen lokalen MCP-Server unter `servers/local-mcp/`, der von GitHub Copilot (Agent Mode) genutzt werden kann, um Werkzeuge wie `git`, `wgx` und einfache Dateizugriffe auszuführen.

### Schnellstart

1. Einmalig die MCP-Abhängigkeiten installieren:

   ```bash
   tools/mcp-local-setup.sh
   ```

2. Sicherstellen, dass im Repo-Root eine Datei `.mcp/registry.json` existiert, die den lokalen Server einträgt, zum Beispiel:

   ```json
   {
     "version": "1.0",
     "servers": {
       "heimgewebe-local": {
         "type": "process",
         "command": "node",
         "args": ["servers/local-mcp/index.js"],
         "tools": [
           "git",
           "wgx",
           "fs_read",
           "fs_write",
           "wgx_guard",
           "wgx_smoke"
         ]
       }
     }
   }
   ```

3. In deiner IDE (z. B. VS Code mit GitHub Copilot Agent Mode) die MCP-Konfiguration so setzen, dass diese Registry-Datei verwendet wird.

4. In Copilot Chat kannst du dann z. B. schreiben:
   „Nutze das Tool wgx_guard, prüfe dieses Repo und erkläre mir alle Fehler verständlich.“

### Kurz erklärt „für Dummies“
- Der MCP-Server ist eine kleine Brücke zwischen Copilot und deinen lokalen Werkzeugen.
- Du gibst im Chat einen Auftrag (zum Beispiel „starte wgx_guard“).
- Copilot ruft intern eines der Tools im MCP-Server auf (z. B. wgx_guard, git, fs_read).
- Der MCP-Server führt den Befehl lokal im Repo aus und gibt das Ergebnis zurück.
- Copilot übersetzt dieses Ergebnis in normale Sprache und kann dir Zusammenfassungen, Erklärungen oder nächste Schritte vorschlagen.

### Typische Stolperfallen (Fehlerprävention)

**Worauf du achten solltest:**

1. **Skript im falschen Ordner ausführen**
   - Problem: `git rev-parse --show-toplevel` schlägt fehl oder zeigt ein anderes Repo.
   - Lösung: Skript immer aus einem Verzeichnis innerhalb des metarepo ausführen.

2. **Node oder Paketmanager fehlen**
   - Wenn `node`, `pnpm` und `npm` fehlen, bricht das Skript sauber mit Fehlermeldung ab.
   - Lösung: Node installieren (empfohlen Version 20+), und mindestens `npm` im PATH haben.

3. **`servers/local-mcp` noch nicht vorhanden**
   - Dann sagt das Skript dir explizit, dass der MCP-Server-Ordner fehlt → zuerst den vorherigen Patch mit `servers/local-mcp` und `.mcp/registry.json` einspielen.

4. **Falsche `registry.json`**
   - Wenn du Tools in der Registry einträgst, die im MCP-Server noch nicht existieren (z. B. `wgx_guard`), ist das harmlos – Copilot kann sie dann nur nicht aufrufen.
   - Problematisch wird es nur, wenn du die Datei syntaktisch zerschießt (dann meckert Copilot in der MCP-Konfiguration).
