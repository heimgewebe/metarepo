from __future__ import annotations
from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END
from .state import AssistantState
from .tools import _require


def supervisor(state: AssistantState) -> Dict[str, Any]:
    task = (state.get("current_task") or "").lower()
    if any(k in task for k in ["code", "refactor", "rust", "python"]):
        return {"next": "code_agent"}
    if any(k in task for k in ["wissen", "notiz", "paper", "sparql", "graph"]):
        return {"next": "knowledge_agent"}
    return {"next": "done"}


def router(state: AssistantState) -> Literal["code_agent", "knowledge_agent", "done"]:
    return state.get("next", "done")


def code_agent(state: AssistantState) -> Dict[str, Any]:
    msg = (state.get("messages") or [])[-1] if state.get("messages") else {}
    query = msg.get("content", "")
    tool = _require("search_codebase")
    hits = tool(query=query, repo_filter=None)
    return {"result": {"agent": "code", "hits": hits}}


def knowledge_agent(state: AssistantState) -> Dict[str, Any]:
    msg = (state.get("messages") or [])[-1] if state.get("messages") else {}
    q = f"SELECT * WHERE {{ ?s ?p ?o }} LIMIT 5  # derived from: {msg.get('content','')!r}"
    tool = _require("query_knowledge_graph")
    rows = tool(sparql_query=q)
    return {"result": {"agent": "knowledge", "rows": rows}}


def build_graph():
    g = StateGraph(AssistantState)
    # Register all nodes before wiring edges/entry points
    g.add_node("supervisor", supervisor)
    g.add_node("code_agent", code_agent)
    g.add_node("knowledge_agent", knowledge_agent)
    g.add_conditional_edges("supervisor", router, {
        "code_agent": "code_agent",
        "knowledge_agent": "knowledge_agent",
        "done": END,
    })
    g.set_entry_point("supervisor")
    return g.compile()


if __name__ == "__main__":
    graph = build_graph()
    init: AssistantState = {
        "messages": [{"role": "user", "content": "Bitte Code in hausKI nach Error-Handling durchsuchen."}],
        "current_task": "code suche",
    }
    out = graph.invoke(init)
    print(out.get("result"))
