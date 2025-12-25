import json
import pytest
from pathlib import Path

def test_insights_daily_published_constraints():
    """
    Enforces 'notification-only' constraints for insights.daily.published event.
    The payload must be small and contain only reference data (URL, TS), not the heavy data itself.
    """
    example_path = Path("contracts/examples/insights.daily.published.v1.example.json")
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
    assert "ts" in payload, "Missing 'ts' in payload"
    assert "url" in payload, "Missing 'url' in payload"
    assert "generated_at" in payload, "Missing 'generated_at' in payload"

    # Forbidden heavy fields
    forbidden_fields = ["topics", "questions", "deltas", "embeddings"]
    for field in forbidden_fields:
        assert field not in payload, f"Forbidden field '{field}' found in payload. Notification events must not carry data."

    # 3. Type check
    assert data.get("type") == "insights.daily.published", "Incorrect event type"
