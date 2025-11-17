# metarepo · Heimgewebe

![WGX](https://img.shields.io/badge/wgx-enabled-blue) ![Contracts](https://img.shields.io/badge/contracts-v1-pinned) ![CI](https://img.shields.io/badge/ci-reusable--workflows-success)

**metarepo** ist die Zentrale des Heimgewebes: Standards, Vorlagen, Reusable CI und Fleet-Rollout.  
Es koordiniert, härtet und synchronisiert alle Sub-Repos. (weltgewebe ist explizit ausgenommen.)

> Lizenz: `SPDX-License-Identifier: MIT` – siehe [LICENSE](LICENSE)

---

## Rolle & Scope

- **Quelle der Wahrheit** für gemeinsame Templates, Policies und Reusable Workflows
- **Toolchain-Pins** und Installer (z. B. `yq`, `uv`, `just`) für reproduzierbare Builds
- **Fleet-Rollout** via WGX/`just` (Dry-Run/Apply) in alle Heimgewebe-Repos
- **Docs & ADRs** zu Architektur, Contracts, CI-Governance

Nicht Teil des metarepo: produktiver Service-Code oder umfangreiche Projekt-Doku einzelner Repos.

---

## Heimgewebe – Komponenten & Zuständigkeiten (ohne weltgewebe)

- **WGX** – Flotten-Motor/CLI (Schicht 0): Orchestrierung, Doctor/Smoke/Metrics, Start/Watch. Keine KI-Logik.
- **semantAH** – Semantisch (Schicht 1): Knowledge-Graph, Embeddings, `insight/*`, `graph/*`.
- **hausKI** – Operativ (Schicht 2): Orchestrierung/Planung/Ausführung; koordiniert Reviews & Aktionen.
- **sichter** – Reflexiv (Schicht 3): Reviews/Diagnosen → `review/*` (ggf. als State-Updates gemappt).
- **chronik** – Memorativ (Schicht 4): Ingest-API, Persistenz/Audit, Event-Exports.
- **heimlern** – Politisch-Adaptiv (Schicht 5): Policies, Entscheidungen, Lern-Scores → `policy.decision`.
- **leitstand** – Interaktiv (Schicht 5/6): UI/Dashboard, Panels („Heute“, „Wissen“, „PC“, „Musik“, „Außen“), Tages-Digest.
- **mitschreiber** – Dialogisch-Semantisch (Schicht 6): OS-Kontext/Intents → `os.context.*` (JSONL).
- **hausKI-audio** – Audio-Pipeline: VAD/ASR → `audio.events` (Kontextquelle für hausKI, Panels in leitstand).
- **aussensensor** – Außen-Signalaufnahme (Schicht 6): produziert `aussen.event` (JSONL), validiert lokal.
- **tools** – Hilfs-Skripte (Pins, JSONL-Utilities, Merge-Helfer); perspektivisch Konsolidierung mit WGX/Metarepo.
- **vault-gewebe** – Privater Wissensspeicher (außerhalb der Fleet); ggf. Exporte für semantAH.

Empfehlung: In Übersichten/Listen stets **sichter**, **mitschreiber**, **hausKI-audio** explizit nennen.

---

## Datenflüsse & Contracts (JSONL)

Lokaler Event-Bus (Topics u. a. `intent/*`, `graph/*`, `review/*`, `policy/*`, `state/*`, `insight/*`, `error/*`).  
Contracts liegen zentral (Tag **`contracts-v1`**); Producer/Consumer validieren gegen dieselben Schemas.

Beispiele:
- **aussen.event**: Producer `aussensensor` → Consumer `leitstand` (Panel „Außen“)
- **os.context.* / intent/**: Producer `mitschreiber`/`hausKI-audio` → `semantAH` → `hausKI`
- **policy.decision**: Producer `heimlern` → Consumer `hausKI` + Audit in `leitstand`
- **review/***: Producer `sichter` → Audit/State in `leitstand`
- **insight/***: Producer `semantAH` → Consumer `hausKI`/`leitstand`
- **metrics.snapshot**: Producer `WGX` → Consumer `hausKI`/`leitstand`

Naming-Hinweis: Ältere Datei `intent_event.schema.json` ≙ heutiges `intent/*`.  
Vereinheitlichung empfohlen (`intent.event.schema.json`) bzw. klare Doku-Brücke.

**MVP-Abweichung (transparent dokumentiert):**  
`aussensensor` pusht derzeit **auch** direkt zu `heimlern`. Zielbild: nur → `leitstand`, von dort weiter/abholen.

---

## CI/CD-Konventionen

- **Reusable Workflows** aus diesem Repo via `workflow_call`, **statisch gepinnt** (z. B. `@contracts-v1`)
- **Version-Pin-Guard**: prüft `uses:`-Pins auf exakt `@contracts-v1` (keine dynamischen Refs)
- **Deletion-Guards**: blocken Delete/Rename in geschützten Pfaden (z. B. `json/`, `proto/`, `fixtures/`)
- **JSONL-Validierung**: Producer/Fixtures werden über den zentralen AJV-Workflow geprüft
- **Metrics**: einheitlicher Snapshot-Workflow (Fallback-Script solange WGX-Befehl noch nicht überall)

ToDo/Empfehlungen:
- `heimlern`: kleines Fixture + CI-Check für `policy.decision` ergänzen
- Baseline-Security/Dependency-Checks via Templates breiter ausrollen (einheitliche Standards)

---

## Getting started

Voraussetzungen:
- `just` (Orchestrierung) – Kurzinfo: [`docs/tools/just.md`](docs/tools/just.md)
- `uv` (Python Tooling) – `uv sync --frozen`
- `yq` – wird via `scripts/tools/yq-pin.sh` deterministisch gepinnt

Schnellstart:
```bash
uv sync --frozen
just list
WGX_DRY_RUN=1 just up      # Templates/Workflows als Dry-Run in Ziel-Repos prüfen
just smoke                 # schneller Fleet-Health-Check
```

Reusable Workflows (im Ziel-Repo):
```yaml
jobs:
  validate:
    uses: heimgewebe/metarepo/.github/workflows/<reusable>.yml@contracts-v1
    with:
      # inputs …
    secrets: inherit
```

Pins **immer** als Tag, nie als Branch/Variable.

---

## Nächste Iteration

1) Schema-Benennungen vereinheitlichen (`intent_event` → `intent.event`)  
2) Doppel-Push `aussensensor→heimlern` eliminieren (nur via `leitstand`)  
3) WGX `metrics snapshot` überall → Removal der Fallback-Skripte  
4) Baseline-Security/Dependency-Workflows aus Templates in alle Code-Repos

---

## Quick Links
- **Docs-Index:** [`docs/README.md`](docs/README.md)
- Kernkonzepte: [`docs/konzept-kern.md`](docs/konzept-kern.md)
- WGX-Konzept: [`docs/wgx-konzept.md`](docs/wgx-konzept.md)
- Fleet-Gesamtbild: [`docs/heimgewebe-gesamt.md`](docs/heimgewebe-gesamt.md)
- Repo-Matrix: [`docs/repo-matrix.md`](docs/repo-matrix.md)
- Contracts & Versionierung: [`docs/contract-versioning.md`](docs/contract-versioning.md)

Weitere Visuals: [Systemdiagramm (Mermaid)](docs/system-overview.mmd) · [Canvas](docs/canvas/) · [Org-Graph](docs/org-graph.mmd).
