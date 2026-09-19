from __future__ import annotations

import json
from pathlib import Path

import jsonschema


def load_schema() -> dict:
    schema_path = Path(__file__).resolve().parents[1] / "contracts" / "agent.tool.schema.json"
    return json.loads(schema_path.read_text())


def test_tool_call_envelope_schema_accepts_minimal_payload():
    schema = load_schema()
    payload = {
        "tool": "search_codebase",
        "args": {"query": "target-service error handling"},
    }

    jsonschema.validate(instance=payload, schema=schema)


def test_tool_call_envelope_schema_rejects_missing_tool():
    schema = load_schema()
    payload = {
        "args": {"query": "target-service error handling"},
    }

    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Schema should reject payloads without a tool identifier")
