import pytest
from agents.tools import _require, search_codebase, query_knowledge_graph

def test_require_returns_registered_tool():
    # Test that _require returns the correct tool for "search_codebase"
    assert _require("search_codebase") == search_codebase

    # Test that _require returns the correct tool for "query_knowledge_graph"
    assert _require("query_knowledge_graph") == query_knowledge_graph

def test_require_raises_key_error_for_unregistered_tool():
    # Test that _require raises a KeyError with the appropriate message for an unregistered tool name
    with pytest.raises(KeyError, match="tool not registered: unknown_tool"):
        _require("unknown_tool")
