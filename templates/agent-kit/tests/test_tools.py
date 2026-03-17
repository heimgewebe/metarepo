import pytest
from agents.tools import _require, search_codebase, query_knowledge_graph

def test_require_returns_registered_tool():
    # Test that _require returns the correct tool for "search_codebase"
    tool = _require("search_codebase")
    assert tool == search_codebase
    assert callable(tool)

    # Test that _require returns the correct tool for "query_knowledge_graph"
    tool = _require("query_knowledge_graph")
    assert tool == query_knowledge_graph
    assert callable(tool)

def test_require_is_idempotent():
    # Ensure multiple calls return the exact same object
    assert _require("search_codebase") is _require("search_codebase")

def test_require_raises_key_error_for_unregistered_tool():
    # Test that _require raises a KeyError with the appropriate message for an unregistered tool name
    with pytest.raises(KeyError, match="tool not registered: unknown_tool"):
        _require("unknown_tool")
