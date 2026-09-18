# System-Übersicht: Heimgewebe

> Archivhinweis (2026-09-18): Physisch gelöschte Repositories bleiben als historische Namen erhalten; tote GitHub-Repo- und Docs-Links wurden entfernt.

> Detaillierte Version: [`heimgewebe-gesamt.md`](./heimgewebe-gesamt.md)

## Repos & Rollen

| Repo | Rolle | Docs |
| --- | --- | --- |
| [`metarepo`](https://github.com/heimgewebe/metarepo) | Control-Plane, Templates, Contracts | [`docs/`](./) |
| [`wgx`](https://github.com/heimgewebe/wgx) | CLI-Orchestrator | [`docs/`](https://github.com/heimgewebe/wgx/tree/main/docs) |
| `hausKI` | KI-Orchestrator, State | – (historische Repo-Dokumentation nicht mehr online) |
| [`semantAH`](https://github.com/heimgewebe/semantAH) | Semantik, Graph, Insights | [`docs/`](https://github.com/heimgewebe/semantAH/tree/main/docs) |
| `chronik` | Ingest, Persistenz, Audit | – |
| `leitstand` | UI/Dashboard | (geplant) |
| `aussensensor` | Außen-Feeds | – (historische Repo-Dokumentation nicht mehr online) |
| `heimlern` | Policies, Lernen | – (historische Repo-Dokumentation nicht mehr online) |

## End-to-End-Beispiel

Ein typischer Datenfluss, um eine Entscheidung zu lernen:

`aussensensor → chronik → heimlern`.

## Kernprinzipien

-   **Lokal-First:** Alle Komponenten laufen ohne Cloud.
-   **Event-basiert:** Systeme kommunizieren über JSONL-Events, nicht über direkte DB-Verbindungen.
-   **Contracts-First:** Schemas in `metarepo` sind die Wahrheit.
-   **Erklärbarkeit:** Entscheidungen (`heimlern`) und Abläufe (`hausKI`) sind auditierbar.
