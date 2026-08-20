import json

import pytest

from scripts.ai_context.validate_ai_context import validate_one


def _write_context(tmp_path, *, do=None, dont=None):
    payload = {
        "project": {
            "name": "example",
            "summary": "Example repository",
            "role": "test",
        },
        "ai_guidance": {
            "do": ["Keep changes focused"] if do is None else do,
            "dont": ["Change unrelated files"] if dont is None else dont,
        },
    }
    path = tmp_path / ".ai-context.yml"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_accepts_non_empty_string_guidance(tmp_path) -> None:
    path = _write_context(
        tmp_path,
        do=["  Keep changes focused  "],
        dont=["Avoid unrelated changes"],
    )

    assert validate_one(path) == []


@pytest.mark.parametrize("field", ["do", "dont"])
def test_rejects_empty_guidance_lists(tmp_path, field) -> None:
    kwargs = {field: []}
    path = _write_context(tmp_path, **kwargs)

    assert f"ai_guidance.{field} must not be empty" in validate_one(path)


@pytest.mark.parametrize("field", ["do", "dont"])
def test_rejects_non_list_guidance(tmp_path, field) -> None:
    kwargs = {field: "single rule"}
    path = _write_context(tmp_path, **kwargs)

    assert (
        f"ai_guidance.{field} must be a non-empty list of non-empty strings"
        in validate_one(path)
    )


@pytest.mark.parametrize("bad_value", [None, 42, {"rule": "nested"}, ["nested"]])
def test_rejects_non_string_guidance_entries(tmp_path, bad_value) -> None:
    path = _write_context(tmp_path, do=[bad_value])

    assert "ai_guidance.do[0] must be a non-empty string" in validate_one(path)


@pytest.mark.parametrize("field", ["do", "dont"])
def test_rejects_blank_guidance_entries(tmp_path, field) -> None:
    kwargs = {field: [" \t "]}
    path = _write_context(tmp_path, **kwargs)

    assert f"ai_guidance.{field}[0] must be a non-empty string" in validate_one(path)
