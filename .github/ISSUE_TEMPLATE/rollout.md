---
name: Fleet rollout – contracts v1
about: Checkliste für das Anheben eines Repos auf contracts-v1
labels: ["contracts-v1", "fleet"]
---

> Markiere nicht zutreffende Punkte mit _N/A_. Die Checkliste dient als Abnahme-Gate für Producer & Consumer.

## Basisdaten
- [ ] Branch `feat/contracts-v1` vorhanden
- [ ] Reusable Workflow `contracts-validate` eingebunden (`heimgewebe/metarepo@contracts-v1`)
- [ ] Repo-spezifische Tests/CI grün

## Producer-Aufgaben
- [ ] **wgx** – `wgx metrics snapshot --json` erzeugt gültiges Artefakt (`metrics.snapshot.schema.json`)
- [ ] **wgx** – Optionaler POST (`--post $INGEST_URL`) funktioniert
- [ ] **semantAH** – `vault/.gewebe/insights/today.json` (≤10 KB) validiert gegen `insights.schema.json`
- [ ] **hausKI-audio** – Events `audio.session_*`, `audio.latency_ms` validieren gegen `audio.events.schema.json`
- [ ] **aussensensor/weltgewebe** – `export/feed.jsonl` folgt `aussen.event.schema.json`

## Consumer-Aufgaben
- [ ] **hausKI** – Endpunkte `/v1/ingest/metrics`, `/v1/policy/decide`, `/v1/policy/feedback` aktiv
- [ ] **hausKI** – JSONL Event-Log `~/.hauski/events/YYYY-MM.jsonl` validiert gegen `event.line.schema.json`
- [ ] **chronik** – `POST /ingest/{domain}` appends nach `data/{domain}.jsonl`
- [ ] **leitstand** (UI) – Panels „Heute/Wissen/PC/Musik/Außen“ zeigen valide Daten, inkl. `why`
- [ ] **heimlern** – `policy.decision.schema.json` implementiert (`Decide` + `Feedback`), Beispiel integriert

## Dokumentation & Enablement
- [ ] README/Docs verweisen auf `docs/contracts.md`
- [ ] Rewards/Policies pro Domain dokumentiert
- [ ] Feature-Flag `policy.enable` standardmäßig auf Shadow Mode (falls neu)

## Abschluss
- [ ] Reviewer bestätigt lokale Tests (Panels/Metrics)
- [ ] CI `contracts-validate` & `wgx-metrics` (falls zutreffend) grün
- [ ] „Warum wurde X empfohlen?“ sichtbar im leitstand (UI)
