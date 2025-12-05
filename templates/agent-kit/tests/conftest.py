"""Test helpers to make the template self-contained during repository-wide runs."""
from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

# Ensure the template package is importable when running pytest from the repo root.
TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
if str(TEMPLATE_ROOT) not in sys.path:
    sys.path.insert(0, str(TEMPLATE_ROOT))


# Provide a lightweight jsonschema stub so tests can run without installing extras.
# The stub covers the minimal checks exercised by the template tests; it is not a
# full JSON Schema implementation.
class _ValidationError(Exception):
    pass


def _validate(instance: dict, schema: dict) -> None:
    required = schema.get("required", [])

    # Generic presence checks for required keys
    for key in required:
        if key not in instance:
            raise _ValidationError(f"{key} is required")

    # Template-specific shape checks used in tests
    if "tool" in required:
        tool_value = instance.get("tool")
        if not isinstance(tool_value, str) or not tool_value:
            raise _ValidationError("tool must be a non-empty string")


# Only register the stub if jsonschema is missing.
try:
    import jsonschema as _jsonschema  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised in repo-level test runs
    stub = ModuleType("jsonschema")
    stub.ValidationError = _ValidationError
    stub.validate = _validate
    sys.modules["jsonschema"] = stub

