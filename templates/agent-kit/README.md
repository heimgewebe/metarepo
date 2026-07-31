# agent-kit (Template)

Minimaler Multi-Agent-Skeleton mit LangGraph für heimgewebe-Repos.

## Ziele
- Lokaler, reproduzierbarer Start mit `uv`.
- Klarer State-Graph: **supervisor → spezial-Agenten → tools**.
- Tool-Calls über strikt definierte JSON-Contracts (`contracts/*.schema.json`).
- Checkpoint-Persistenz ist standardmäßig deaktiviert; Aktivierung erfordert eine separat geprüfte Serializer- und Vertrauensgrenzen-Policy.

## Quickstart
```bash
uv sync --frozen
uv run -m agents.graph  # startet eine Mini-Demo
```

## Befehle (Just)
```bash
just agents.run     # Demo starten
just agents.test    # Tests
```

## Struktur
```
agent-kit/
  pyproject.toml
  agents/
    __init__.py
    graph.py
    tools.py
    state.py
  tests/
    test_graph.py
  contracts/
    agent.tool.schema.json
```

## Notizen
- LangGraph ist bewusst klein gehalten (Supervisor + 2 Platzhalter-Agenten).
- Tools sind reine Funktionen mit **striktem Input/Output** gemäß `agent.tool.schema.json`.
