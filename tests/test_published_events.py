import json
import pytest
from pathlib import Path

# Notification-only event size limit (2KB)
MAX_NOTIFICATION_EVENT_SIZE_BYTES = 2048

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = REPO_ROOT / "contracts"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"
EVENT_SCHEMAS_DIR = CONTRACTS_DIR / "events"

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def _schema_path_for_example(example_path: Path, doc: dict) -> Path:
    """
    Derives the schema path.
    1. Try from 'type' field in the document: contracts/events/<type>.schema.json
    2. Fallback to filename: contracts/examples/<name>.example.json -> contracts/events/<name>.schema.json
    """
    # 1. Try deriving from 'type' field
    event_type = doc.get("type")
    if event_type and isinstance(event_type, str):
        event_type = event_type.strip()
        if event_type:
            schema_candidate = EVENT_SCHEMAS_DIR / f"{event_type}.schema.json"
            if schema_candidate.exists():
                return schema_candidate

    # 2. Fallback: Derive from filename
    schema_name = example_path.name.replace(".example.json", ".schema.json")
    return EVENT_SCHEMAS_DIR / schema_name

def _allowed_payload_keys_from_schema(schema_path: Path, schema: dict) -> set[str]:
    """
    Extract allowed payload keys from an event schema:
      schema.properties.payload.properties => allowed keys
    """
    props = schema.get("properties")
    if not isinstance(props, dict):
        pytest.fail(f"{schema_path.name}: Schema missing top-level 'properties' object")

    payload = props.get("payload")
    if not isinstance(payload, dict):
        pytest.fail(f"{schema_path.name}: Schema missing 'properties.payload' object")

    payload_props = payload.get("properties")
    if not isinstance(payload_props, dict):
        # If schema intentionally allows any payload keys, it should say so explicitly.
        pytest.fail(f"{schema_path.name}: Schema missing 'properties.payload.properties' object")

    # If schema claims payload is strict, it should declare additionalProperties=false.
    addl = payload.get("additionalProperties", None)
    if addl is not False:
        pytest.fail(
            f"{schema_path.name}: Test requirement: for strict published.v1 payload examples, the schema must set "
            "'properties.payload.additionalProperties': false to lock down allowed keys. "
            "JSON Schema allows omitting 'additionalProperties' (defaults to true) or using a schema "
            "object; this suite enforces the stricter convention for published.v1 payloads."
        )

    return set(payload_props.keys())

def test_knowledge_observatory_published_constraints():
    """
    Enforces 'notification-only' constraints for knowledge.observatory.published.v1 event.
    The payload must be small and contain only reference data (URL, TS), not the heavy data itself.
    """
    example_path = EXAMPLES_DIR / "knowledge.observatory.published.v1.example.json"
    if not example_path.exists():
        pytest.fail(f"Example file not found: {example_path}")

    with open(example_path, "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content)

    # 1. Size constraint (Notification should be lightweight)
    size_bytes = len(content.encode("utf-8"))
    assert size_bytes < MAX_NOTIFICATION_EVENT_SIZE_BYTES, \
        f"Event payload too large ({size_bytes} bytes). Must be < {MAX_NOTIFICATION_EVENT_SIZE_BYTES} bytes for notification-only events."

    # 2. Structure constraint
    payload = data.get("payload", {})

    # Required reference fields
    assert "url" in payload, "Missing 'url' in payload"

    # Forbidden heavy fields (from knowledge.observatory.schema.json)
    forbidden_fields = ["topics", "signals", "blind_spots", "considered_but_rejected", "observatory_id"]
    for field in forbidden_fields:
        assert field not in payload, f"Forbidden field '{field}' found in payload. Notification events must not carry data."

    # 3. Type check
    assert data.get("type") == "knowledge.observatory.published.v1", "Incorrect event type"

    # 4. Source is non-empty
    assert data.get("source") and len(data.get("source", "")) > 0, "Source must be non-empty"

    # 5. Timestamp is present
    assert "timestamp" in data, "Missing 'timestamp' field"


def test_published_v1_strict_payload_enforcement():
    """
    Documentation test: demonstrates that published.v1 events typically adhere to a strict payload structure.

    This test serves as an executable convention documentation. It explicitly lists the fields
    historically expected in published.v1 events (url, generated_at, ts).
    Note that the definitive validation logic is in test_all_published_examples_comply_with_strict_payload,
    which derives rules directly from the schema.
    """
    # Valid event with only allowed fields
    valid_event = {
        "type": "insights.daily.published.v1",
        "source": "semantAH",
        "timestamp": "2025-12-25T06:05:00Z",
        "payload": {
            "url": "https://example.com/insights.json",
            "generated_at": "2025-12-25T06:00:00Z"
        }
    }
    
    # This assertion mirrors the expected minimal structure for published.v1 events.
    # We check against a known subset to document the "core" fields.
    assert set(valid_event["payload"].keys()).issubset({"url", "generated_at", "ts"}), \
        "Payload can only contain url, generated_at (and optionally ts)"


def test_all_published_examples_comply_with_strict_payload():
    """
    Ensures all published.v1 event examples comply with the strict payload requirement defined in their schemas.
    """
    # Iterate over all *.published.v1.example.json files
    for example_path in EXAMPLES_DIR.glob("*.published.v1.example.json"):
        doc = _load_json(example_path)

        payload = doc.get("payload", {})
        assert isinstance(payload, dict), f"{example_path.name}: payload must be an object"

        # Derive schema path
        schema_path = _schema_path_for_example(example_path, doc)
        assert schema_path.exists(), (
            f"{example_path.name}: missing schema at {schema_path}"
        )

        schema = _load_json(schema_path)
        allowed = _allowed_payload_keys_from_schema(schema_path, schema)

        got = set(payload.keys())
        forbidden = got - allowed
        assert not forbidden, (
            f"{example_path.name}: payload has forbidden keys: {forbidden}; allowed: {sorted(allowed)}"
        )

        # Check for required payload keys
        required = schema.get("properties", {}).get("payload", {}).get("required", [])
        required_set = set(required) if isinstance(required, list) else set()

        missing = required_set - got
        assert not missing, (
            f"{example_path.name}: payload missing required keys: {missing}; required: {sorted(required_set)}"
        )
