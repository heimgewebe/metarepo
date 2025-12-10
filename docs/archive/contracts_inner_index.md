# Index: Heimgewebe Contracts

> **Quelle:** [`/contracts`](../../contracts/) im Root-Verzeichnis.

| Schema | Kurzbeschreibung | Producer | Consumer |
| --- | --- | --- | --- |
| [`contracts/agent.workflow.schema.json`](../../contracts/agent.workflow.schema.json) | Workflow-Definition für `wgx agent` | `wgx agent` | `wgx agent run/trace` |
| [`contracts/dev.tooling.schema.json`](../../contracts/dev.tooling.schema.json) | Metadaten für Werkzeuge, genutzt von `wgx doctor` | `wgx`, IDE | `wgx doctor` |
| [`contracts/aussen.event.schema.json`](../../contracts/aussen.event.schema.json) | Außenereignisse (Links, Beobachtungen, Scores) | `aussensensor`, `weltgewebe` | `chronik`, Exporte |
| [`contracts/policy.decision.schema.json`](../../contracts/policy.decision.schema.json) | Entscheidungen einer Policy inkl. Begründung | `heimlern` | `hausKI`, `chronik` |
| [`contracts/policy.feedback.schema.json`](../../contracts/policy.feedback.schema.json) | Feedback auf eine Entscheidung (Reward, Notizen) | `leitstand` (UI), Operator:innen | `heimlern` |
| [`contracts/metrics.snapshot.schema.json`](../../contracts/metrics.snapshot.schema.json) | Systemmetriken aus `wgx` | `wgx` | `hausKI`, `chronik` |
| [`contracts/insights.schema.json`](../../contracts/insights.schema.json) | Wissens-Exports | `semantAH` | `hausKI`, `chronik` |
| [`contracts/audio.events.schema.json`](../../contracts/audio.events.schema.json) | Audio-/Telemetrie-Events | `hauski-audio` | `hausKI`, `chronik` |

---
- **Kontext `mitschreiber`:** [Details zu `os.context.*`](../contracts/mitschreiber.md)
- **Kontext `sichter`:** [Details zu `review.*` und `feedback.*`](../contracts/sichter.md)
