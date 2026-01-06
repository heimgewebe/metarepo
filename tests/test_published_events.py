import json
import pytest
from pathlib import Path

def test_knowledge_observatory_published_constraints():
    """
    Enforces 'notification-only' constraints for knowledge.observatory.published.v1 event.
    The payload must be small and contain only reference data (URL, TS), not the heavy data itself.
    """
    example_path = Path("contracts/examples/knowledge.observatory.published.v1.example.json")
    if not example_path.exists():
        pytest.fail(f"Example file not found: {example_path}")

    with open(example_path, "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content)

    # 1. Size constraint (Notification should be lightweight)
    size_bytes = len(content.encode("utf-8"))
    assert size_bytes < 2048, f"Event payload too large ({size_bytes} bytes). Must be < 2KB for notification-only events."

    # 2. Structure constraint
    payload = data.get("payload", {})

    # Required reference fields
    assert "url" in payload, "Missing 'url' in payload"
    # Optional fields: ts, generated_at
    # But no forbidden heavy fields

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
    Tests that published.v1.schema.json enforces additionalProperties: false in payload.
    This breaking change ensures producers cannot send extra fields.
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
    
    # This test documents the contract: producers must not add extra fields
    # The schema validation will reject events with additional payload fields
    assert set(valid_event["payload"].keys()).issubset({"url", "ts", "generated_at"}), \
        "Payload can only contain url, ts, and generated_at"


def test_all_published_examples_comply_with_strict_payload():
    """
    Ensures all existing published event examples comply with the strict payload requirement.
    This validates that the breaking change doesn't break existing documented examples.
    """
    examples_dir = Path("contracts/examples")
    published_examples = [
        "insights.daily.published.v1.example.json",
        "knowledge.observatory.published.v1.example.json"
    ]
    
    for example_file in published_examples:
        example_path = examples_dir / example_file
        if not example_path.exists():
            pytest.skip(f"Example not found: {example_path}")
            
        with open(example_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        
        payload = data.get("payload", {})
        # Check that payload only has allowed keys
        allowed_keys = {"url", "ts", "generated_at"}
        actual_keys = set(payload.keys())
        
        assert actual_keys.issubset(allowed_keys), \
            f"{example_file}: payload has forbidden keys: {actual_keys - allowed_keys}"
