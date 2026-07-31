from agents.graph import build_graph


def test_build_graph_compiles():
    graph = build_graph()
    assert graph is not None


def test_checkpoint_persistence_is_disabled_by_default():
    graph = build_graph()
    assert graph.checkpointer is None


def test_supervisor_registered_node():
    graph = build_graph()
    out = graph.invoke({"messages": [], "current_task": ""})
    assert isinstance(out, dict)


def test_route_and_invoke_code_path():
    graph = build_graph()
    init = {
        "messages": [{"role": "user", "content": "Finde Error-Handling in hausKI"}],
        "current_task": "code suche",
    }
    out = graph.invoke(init)
    assert out.get("result", {}).get("agent") == "code"


def test_route_and_invoke_knowledge_path():
    graph = build_graph()
    init = {
        "messages": [{"role": "user", "content": "Was steht im Wissensgraph zu hausKI?"}],
        "current_task": "wissen abfrage",
    }
    out = graph.invoke(init)
    assert out.get("result", {}).get("agent") == "knowledge"


def test_supervisor_falls_through_to_done():
    graph = build_graph()
    init = {
        "messages": [{"role": "user", "content": "Nur plaudern"}],
        "current_task": "smalltalk",
    }
    out = graph.invoke(init)
    assert out.get("result") is None
