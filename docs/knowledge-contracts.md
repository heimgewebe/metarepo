# Knowledge-Graph Contracts – Kurzleitfaden

**Zweck:** Strukturierter Export von Wissen aus Code/Docs/ADRs als Graph für `semantAH` & `leitstand` (UI).

**Schema:** `contracts/knowledge.graph.schema.json`

## Minimalbeispiel
```json
{
  "nodes": [
    {"id": "mod:hauski", "node_type": "code_entity", "label": "hausKI core"}
  ],
  "edges": [
    {"source": "mod:hauski", "relation": "references", "target": "doc:contracts"}
  ],
  "metadata": { "tags": ["demo"] }
}
```

## Erzeugung (Beispiel)
```bash
wgx knowledge extract            # schreibt knowledge.graph.json
wgx knowledge validate           # prüft gegen Schema
```

## CI-Einbindung
Nutze den bereitgestellten Workflow `.github/workflows/validate-knowledge-graph.yml` aus dem Metarepo (siehe `docs/contracts.md`).
