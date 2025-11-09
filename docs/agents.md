# IDEal Agents – Mini-Orchestrierung

Die Agent-Pipeline erlaubt das lokale Ausführen einfacher Workflows (sequential/parallel) und erzeugt einen JSONL-Trace unter `.agents/runs/`.

## Schnellstart

```bash
just agent-run                           # nutzt agents/sample.workflow.json
just agent-run ARG=agents/foo.json     # eigenes Workflow-File
just agent-trace                         # zeigt letzten Run als Tabelle
just agent-trace FILE=.agents/runs/<id>.jsonl
```

Äquivalent mit WGX:

```bash
scripts/wgx agent run agents/sample.workflow.json
scripts/wgx agent trace
```

## Inputs & Policies
- Workflow-Datei: JSON (siehe `templates/agents/sample.workflow.json`)
- Orchestration: `sequential` oder `parallel`
- Policies: `timeout_sec`, `retry_strategy.max_retries`, `retry_strategy.backoff (none|fixed|exponential)`

## Artefakte
- Trace: `.agents/runs/<timestamp-rand>.jsonl` (jedes Event = 1 Zeile JSON)
- CI-Smoketest: `templates/.github/workflows/agent-smoke.yml`

## Nächste Schritte
- Validierung gegen `contracts/agent.workflow.schema.json` (sobald verfügbar) via reusable AJV-Workflow
- Hooks: Vor-/Nachschritte (z. B. `wgx code lint`, `wgx knowledge validate`) in Agents integrieren
