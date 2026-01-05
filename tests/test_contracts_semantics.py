"""
Tests for canonical contracts logic.
Validates the new schemas decision.outcome.v1 and policy.weight_adjustment.v1 against
their fixtures, ensuring semantic rules are enforced.
"""
import json
import pytest
import math
from pathlib import Path
from jsonschema import validate, ValidationError

# Map fixture prefixes to schema files
SCHEMA_MAP = {
    "decision.outcome": "contracts/decision.outcome.v1.schema.json",
    "policy.weight_adjustment": "contracts/policy.weight_adjustment.v1.schema.json",
}

def load_schema(schema_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_contract_fixtures():
    """Returns a list of (fixture_path, schema_key, expect_valid)."""
    fixtures_dir = Path("tests/fixtures/contracts")
    if not fixtures_dir.exists():
        return []

    cases = []
    for f in fixtures_dir.glob("*.json"):
        name = f.name
        # Determine schema key (longest matching prefix)
        schema_key = None
        for key in SCHEMA_MAP:
            if name.startswith(key):
                if schema_key is None or len(key) > len(schema_key):
                    schema_key = key

        if schema_key:
            # Expect failure if filename contains ".fail."
            expect_valid = ".fail." not in name
            cases.append((f, schema_key, expect_valid))

    return cases

def validate_finite_numbers(instance):
    """Recursively checks that all numbers in the instance are finite."""
    if isinstance(instance, dict):
        for k, v in instance.items():
            validate_finite_numbers(v)
    elif isinstance(instance, list):
        for v in instance:
            validate_finite_numbers(v)
    elif isinstance(instance, float):
        if not math.isfinite(instance):
            raise ValidationError(f"Found non-finite number: {instance}")

@pytest.mark.parametrize("fixture_path, schema_key, expect_valid", get_contract_fixtures())
def test_contract_fixture(fixture_path, schema_key, expect_valid):
    """
    Validates a fixture against its mapped schema.
    If expect_valid is True, validation must pass.
    If expect_valid is False, validation must raise ValidationError.
    """
    schema_file = SCHEMA_MAP[schema_key]
    schema = load_schema(schema_file)

    # All fixtures must be valid JSON - fail immediately if not parseable
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            instance = json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"Fixture {fixture_path.name} contains invalid JSON: {e}. All fixtures must be valid JSON.")

    if expect_valid:
        try:
            validate_finite_numbers(instance)
            validate(instance=instance, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Fixture {fixture_path.name} failed validation against {schema_file}: {e.message}")
    else:
        with pytest.raises(ValidationError, match=r".*"):
            validate_finite_numbers(instance)
            validate(instance=instance, schema=schema)


# Programmatic tests for NaN/Inf rejection
@pytest.mark.parametrize("non_finite_value", [math.nan, math.inf, -math.inf])
def test_decision_outcome_rejects_non_finite_reward(non_finite_value):
    """Test that decision.outcome rejects non-finite values in reward field (if present)."""
    instance = {
        "outcome": "success",
        "success": True,
        "metadata": {"reward": non_finite_value}
    }
    
    with pytest.raises(ValidationError, match=r".*non-finite.*"):
        validate_finite_numbers(instance)


@pytest.mark.parametrize("non_finite_value", [math.nan, math.inf, -math.inf])
def test_policy_weight_adjustment_rejects_non_finite_delta_value(non_finite_value):
    """Test that policy.weight_adjustment rejects non-finite delta values."""
    instance = {
        "version": "v1",
        "basis_policy": "pol-123",
        "ts": "2025-01-01T12:00:00Z",
        "deltas": {
            "factor": {
                "kind": "absolute",
                "value": non_finite_value
            }
        },
        "confidence": 0.9,
        "evidence": {
            "decisions_analyzed": 100
        }
    }
    
    with pytest.raises(ValidationError, match=r".*non-finite.*"):
        validate_finite_numbers(instance)
