# Repo-Matrix (Rolle • Status • Schnittstellen)

> Quelle der Fleet-Liste: [`repos.yml`](../repos.yml). Bitte dortige Ergänzungen/Entfernungen hier spiegeln.

| Repo | Rolle | Domain (repos.yml)* | Scope (repos.yml)* | Status |
| --- | --- | --- | --- | --- |
| **metarepo** | Control-Plane (Templates, Reusables, Contracts) | – | – | stabil |
| **wgx** | Orchestrator (CLI) | platform | metrics | aktiv |
| **hausKI** | KI-Orchestrator (Rust, GPU, Offline) | assistant | policy | aktiv |
| **hausKI-audio** | Audio-Pipeline | audio | events | MVP |
| **semantAH** | Semantik & Graph | insights | export | Aufbau |
| **chronik** | Event-Ingest + Persistenz/Audit (vormals leitstand) | chronik | ingest | stabil |
| **leitstand** | UI/Dashboard (geplant) | ui | dashboard | geplant |
| **aussensensor** | Feeds → Chronik | aussen | events | aktiv (Daemon geplant) |
| **heimlern** | Policies/Bandit | policy | library | Experiment |
| **weltgewebe** | Web (docs-first, Gates) | aussen | events | Docs-only |
| **tools** | Hilfsskripte & Shared Utilities | tooling | shared | aktiv |
| **vault-gewebe** | Obsidian Vault | – | – | kuratiert |

## Schnittstellenverträge (Auswahl)
- Außen-Events (JSONL): `contracts/aussen.event.schema.json` (aktuell über Tag `contracts-v1` ausgespielt)
- Insights & Tageszusammenfassungen: `contracts/insights.schema.json`, `contracts/insights.daily.schema.json`
- Metrics Snapshot: `contracts/metrics.snapshot.schema.json`
- Policy-Entscheidungen: `contracts/policy.decision.schema.json`

* *Domain/Scope-Spalten sind deskriptiv gedacht. Sie sind derzeit **keine** verpflichtenden Felder im* [`docs/repos.yml.md`](./repos.yml.md) *beschriebenen Schema und dienen nur zur Einordnung.*

