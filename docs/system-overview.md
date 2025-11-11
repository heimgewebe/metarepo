# Systemübersicht (Heimgewebe)

Diese Seite bündelt die wichtigsten Einstiege ins Heimgewebe-Ökosystem. Sie ergänzt den
[Docs-Index](./README.md) um einen schnellen Überblick über Repos, Verantwortlichkeiten und
weiterführende Dokumente.

## Kern-Repos & Rollen

| Repo | Rolle | Primäre Doku |
| --- | --- | --- |
| [`metarepo`](https://github.com/heimgewebe/metarepo) | Control-Plane, Templates, Contracts | [Docs-Index](./README.md) |
| [`wgx`](https://github.com/heimgewebe/wgx) | Fleet-Orchestrierung & Maschinenpflege | [`docs/`](https://github.com/heimgewebe/wgx/tree/main/docs) |
| [`hausKI`](https://github.com/heimgewebe/hausKI) | Orchestrator, Decision-Loop, Persistenz | [`docs/`](https://github.com/heimgewebe/hausKI/tree/main/docs) |
| [`hauski-audio`](https://github.com/heimgewebe/hauski-audio) | Audio-/Telemetrie-Pipelines | [`docs/`](https://github.com/heimgewebe/hauski-audio/tree/main/docs) |
| [`leitstand`](https://github.com/heimgewebe/leitstand) | Ingest, Panels, JSONL-Ablage | [`docs/`](https://github.com/heimgewebe/leitstand/tree/main/docs) |
| [`aussensensor`](https://github.com/heimgewebe/aussensensor) | Externe Signale → kuratierte Events | [`docs/`](https://github.com/heimgewebe/aussensensor/tree/main/docs) |
| [`heimlern`](https://github.com/heimgewebe/heimlern) | Bandit-Policies, Feedback, Snapshots | [`docs/`](https://github.com/heimgewebe/heimlern/tree/main/docs) |
| [`semantAH`](https://github.com/heimgewebe/semantAH) | Wissensaufbereitung, Graph, Exporte | [`docs/`](https://github.com/heimgewebe/semantAH/tree/main/docs) |
| [`mitschreiber`](https://github.com/heimgewebe/mitschreiber) | Intent-/Kontext-Sensorik | [`docs/`](https://github.com/heimgewebe/mitschreiber/tree/main/docs) |

> 💡 `vault-gewebe` ist privat; Dokumentation erfolgt bewusst nicht öffentlich.

## Navigations-Hinweise

- Architektur & Datenflüsse: siehe [Architektur](./architecture.md) sowie die Mermaids unter
  [`docs/heimgewebe-architektur.mmd`](./heimgewebe-architektur.mmd) und
  [`docs/heimgewebe-dataflow.mmd`](./heimgewebe-dataflow.mmd).
- Contracts & Schemas: Einstiege in [Events & Contracts](./contracts/index.md) sowie die
  JSON-Schemas unter [`contracts/`](../contracts).
- Automatisierung: Übersicht in [Automatisierung & CI](./automation.md) und Details in
  [`docs/ci-reusables.md`](./ci-reusables.md) bzw. [`docs/fleet.md`](./fleet.md).
- Troubleshooting & Runbooks: siehe [Troubleshooting & FAQ](./troubleshooting.md) und
  [`docs/runbooks.md`](./runbooks.md).
- End-to-End-Beispiel: [docs/e2e.md](./e2e.md) beschreibt den automatisierten Lauf
  `aussensensor → leitstand → heimlern`.

## Wie finde ich Sub-Repo-Dokumentation?

1. Wähle das Ziel-Repo in der Tabelle oben und folge dem verlinkten `docs/`-Verzeichnis.
2. Die meisten Repos enthalten eine `README.md` oder einen `guide.md` Einstieg, häufig ergänzt um
   `docs/runbooks/` oder `docs/contracts/` Unterordner.
3. Für Fragen zur Fleet-weiten Governance hilft der Metarepo-Dokumentationsindex
   ([Docs-Index](./README.md)) weiter.

## Weitere Ressourcen

- [Org-Index](./org-index.md) – Inventar aller Repos mit Status & Ownership.
- [Repo-Matrix](./repo-matrix.md) – Detailtabelle (Maintainer, Deploy-Status, Health).
- [Heimgewebe – Überblick](./heimgewebe-gesamt.md) – Narrative Gesamtdarstellung.
- [Vision](./vision.md) – Leitplanken & mittel-/langfristige Ziele.
