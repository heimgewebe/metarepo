# System-Übersicht: Heimgewebe

> Detaillierte Version: [`heimgewebe-gesamt.md`](./heimgewebe-gesamt.md)

## Repos & Rollen

| Repo | Rolle | Docs |
| --- | --- | --- |
| [`metarepo`](https://github.com/heimgewebe/metarepo) | Control-Plane, Templates, Contracts | [`docs/`](./) |
| [`wgx`](https://github.com/heimgewebe/wgx) | CLI-Orchestrator | [`docs/`](https://github.com/heimgewebe/wgx/tree/main/docs) |
| [`hausKI`](https://github.com/heimgewebe/hausKI) | KI-Orchestrator, State | [`docs/`](https://github.com/heimgewebe/hausKI/tree/main/docs) |
| [`semantAH`](https://github.com/heimgewebe/semantAH) | Semantik, Graph, Insights | [`docs/`](https://github.com/heimgewebe/semantAH/tree/main/docs) |
| [`chronik`](https://github.com/heimgewebe/chronik) | Ingest, Persistenz, Audit | [`docs/`](https://github.com/heimgewebe/chronik/tree/main/docs) |
| [`leitstand`](https://github.com/heimgewebe/leitstand) | UI/Dashboard | (geplant) |
| [`aussensensor`](https://github.com/heimgewebe/aussensensor) | Außen-Feeds | [`docs/`](https://github.com/heimgewebe/aussensensor/tree/main/docs) |
| [`heimlern`](https://github.com/heimgewebe/heimlern) | Policies, Lernen | [`docs/`](https://github.com/heimgewebe/heimlern/tree/main/docs) |

## End-to-End-Beispiel

Ein typischer Datenfluss, um eine Entscheidung zu lernen:

`aussensensor → chronik → heimlern`.

## Kernprinzipien

-   **Lokal-First:** Alle Komponenten laufen ohne Cloud.
-   **Event-basiert:** Systeme kommunizieren über JSONL-Events, nicht über direkte DB-Verbindungen.
-   **Contracts-First:** Schemas in `metarepo` sind die Wahrheit.
-   **Erklärbarkeit:** Entscheidungen (`heimlern`) und Abläufe (`hausKI`) sind auditierbar.
