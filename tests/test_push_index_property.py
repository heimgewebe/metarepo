"""Tests for push_index_property batching helpers."""

from __future__ import annotations

import importlib
import math
from typing import Any

import pytest

try:  # Prefer real pandas when available.
    import pandas as pd  # type: ignore[no-redef]
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal envs
    from metarepo_tools import pdmini as pd

try:
    from metarepo_tools.push_index_property import to_batches as _direct_to_batches
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal envs
    _direct_to_batches = None


_CANDIDATE_MODULES = (
    "push_index_property",
    "tools.push_index_property",
    "heimgewebe.tools.push_index_property",
    "heimgewebe_tools.push_index_property",
    "metarepo_tools.push_index_property",
)


def _load_push_index_module() -> Any:
    """Load the push_index_property module from one of several candidate paths."""

    for module_name in _CANDIDATE_MODULES:
        try:
            module = importlib.import_module(module_name)
            module.__dict__.setdefault("__loaded_from__", module_name)
            return module
        except ModuleNotFoundError:
            continue
    return None


push_index_property = _load_push_index_module()

if push_index_property is None:
    pytest.skip(
        "push_index_property module not available; skipping push index tests",
        allow_module_level=True,
    )


if _direct_to_batches is not None:
    to_batches = _direct_to_batches
else:
    to_batches = push_index_property.to_batches


@pytest.mark.parametrize(
    ("namespace_value", "expected"),
    [
        (None, "vault-default"),
        ("", "vault-default"),
        ("   ", "vault-default"),
        (math.nan, "vault-default"),
        ("vault", "vault"),
    ],
    ids=["None", "empty", "spaces", "nan", "value"],
)
def test_default_namespace_applied(namespace_value: object, expected: str) -> None:
    df = pd.DataFrame(
        [
            {
                "doc_id": "D",
                "namespace": namespace_value,
                "text": "x",
                "embedding": [0.1, 0.2],
            }
        ]
    )

    batches = list(to_batches(df, default_namespace="vault-default"))

    assert len(batches) == 1
    assert batches[0]["namespace"] == expected


def test_columnar_mapping_consumes_iterables() -> None:
    payload = {
        "doc_id": (f"doc-{i}" for i in range(2)),
        "namespace": (None for _ in range(2)),
        "text": (f"text-{i}" for i in range(2)),
        "embedding": ([0.1, 0.2] for _ in range(2)),
    }

    batches = list(to_batches(payload, default_namespace="vault-default"))

    assert [batch["doc_id"] for batch in batches] == ["doc-0", "doc-1"]
    assert all(batch["namespace"] == "vault-default" for batch in batches)
    assert [batch["chunks"][0]["text"] for batch in batches] == ["text-0", "text-1"]


def test_sequence_like_accepts_iterators_and_sequences_only() -> None:
    assert push_index_property._is_sequence_like([1, 2, 3])
    assert push_index_property._is_sequence_like((i for i in range(2)))
    assert push_index_property._is_sequence_like(iter(range(1)))

    assert not push_index_property._is_sequence_like({"a", "b"})
    assert not push_index_property._is_sequence_like({"k": "v"})
    assert not push_index_property._is_sequence_like("text")


def test_columnar_mapping_requires_all_values_to_be_sequence_like() -> None:
    mapping = {"doc_id": ["d1", "d2"], "text": {"a", "b"}}

    assert not push_index_property._looks_like_columnar_mapping(mapping)


def test_batches_shape_and_chunk_ids_clean() -> None:
    """Batches enthalten doc_id, zwei Chunks und keine 'nan'-IDs."""
    df = pd.DataFrame(
        [
            {
                "doc_id": "D",
                "namespace": None,
                "text": "alpha",
                "embedding": [0.1, 0.2],
            },
            {
                "doc_id": "D",
                "namespace": "   ",
                "text": "beta",
                "embedding": [0.2, 0.3],
            },
        ]
    )

    batches = list(to_batches(df, default_namespace="vault-default"))
    assert len(batches) == 1
    batch = batches[0]

    # Grundform
    assert batch["doc_id"] == "D"
    assert batch["namespace"] == "vault-default"
    assert "chunks" in batch and isinstance(batch["chunks"], list)
    assert len(batch["chunks"]) == 2

    # Chunk-ID Hygiene
    for chunk in batch["chunks"]:
        cid = str(chunk["id"])
        assert cid, "chunk id must be non-empty"
        low = cid.lower()
        assert low != "nan" and "nan" not in low


def test_doc_id_preserved_exactly() -> None:
    """doc_id is trimmed but otherwise unmodified when batching."""
    doc_id = "  MixED Id  "
    df = pd.DataFrame(
        [
            {
                "doc_id": doc_id,
                "namespace": None,
                "text": "payload",
                "embedding": [0.3, 0.4],
            }
        ]
    )

    batches = list(to_batches(df, default_namespace="vault-default"))

    assert len(batches) == 1
    assert batches[0]["doc_id"] == doc_id.strip()


def test_resolve_namespace_precedence() -> None:
    df = pd.DataFrame(
        [
            {
                "doc_id": "a",
                "namespace": "  ns-a  ",
                "text": "t1",
                "embedding": [0.1],
            },
            {
                "doc_id": "a",
                "namespace": None,
                "text": "t2",
                "embedding": [0.2],
            },
        ]
    )

    (batch,) = list(to_batches(df, default_namespace="fallback"))

    assert batch["namespace"] == "ns-a"


def test_resolve_namespace_ignores_nan_and_uses_default() -> None:
    df = pd.DataFrame(
        [
            {
                "doc_id": "b",
                "namespace": math.nan,
                "text": "t",
                "embedding": [0.1],
            }
        ]
    )

    (batch,) = list(to_batches(df, default_namespace="vault-default"))

    assert batch["namespace"] == "vault-default"


def test_metadata_extraction() -> None:
    df = pd.DataFrame(
        [
            {
                "doc_id": "x",
                "namespace": "ns",
                "text": "hello",
                "embedding": [0.1],
                "lang": "de",
                "ver": 1,
            }
        ]
    )

    (batch,) = list(to_batches(df, default_namespace="fallback"))
    (chunk,) = batch["chunks"]

    assert "metadata" in chunk and chunk["metadata"] == {"lang": "de", "ver": 1}


def test_columnar_mapping_is_coerced_to_rows() -> None:
    columnar = {
        "doc_id": ["a", "b"],
        "text": ["hello", "world"],
        "embedding": [[0.1], [0.2]],
    }

    batches = list(to_batches(columnar, default_namespace="ns-default"))

    assert [batch["doc_id"] for batch in batches] == ["a", "b"]
    assert all(batch["namespace"] == "ns-default" for batch in batches)
    assert [chunk["text"] for batch in batches for chunk in batch["chunks"]] == [
        "hello",
        "world",
    ]


def test_columnar_mapping_with_single_column_expands_rows() -> None:
    columnar = {
        "doc_id": ["a", "b", "c"],
    }

    batches = list(to_batches(columnar, default_namespace="ns-default"))

    assert [batch["doc_id"] for batch in batches] == ["a", "b", "c"]
    assert all(batch["namespace"] == "ns-default" for batch in batches)
    assert all(len(batch["chunks"]) == 1 for batch in batches)


@pytest.mark.parametrize(
    "value",
    [None, math.nan],
    ids=["None", "NaN"],
)
def test_normalise_doc_id_missing_values(value: Any) -> None:
    with pytest.raises(ValueError, match="doc_id column is required"):
        push_index_property._normalise_doc_id(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "  ",
        "NaN",
        " null ",
        "NONE",
        "\u00A0",  # non-breaking space
    ],
    ids=["empty", "spaces", "nan-str", "null-str", "none-str", "nbsp"],
)
def test_normalise_doc_id_rejects_sentinel_strings(value: str) -> None:
    with pytest.raises(
        ValueError, match="doc_id must be a non-empty, non-sentinel string"
    ):
        push_index_property._normalise_doc_id(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        ("0", "0"),
        ("  x  ", "x"),
    ],
    ids=["zero-int", "zero-str", "trim"],
)
def test_normalise_doc_id_valid_values(value: Any, expected: str) -> None:
    assert push_index_property._normalise_doc_id(value) == expected
