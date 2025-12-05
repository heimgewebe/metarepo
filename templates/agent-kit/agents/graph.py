from __future__ import annotations
from typing import Literal, Dict, Any, Callable

try:  # pragma: no cover - exercised in repo-level test runs without extras installed
    from langgraph.graph import StateGraph, END
except ModuleNotFoundError:  # Lightweight fallback so the template is runnable without langgraph
    END = "__END__"

    class _CompiledGraph:
        def __init__(
            self,
            entry: str,
            nodes: Dict[str, Callable[["AssistantState"], Dict[str, Any]]],
            conditional_edges: Dict[str, tuple[Callable[["AssistantState"], str], Dict[str, str]]],
        ) -> None:
            self._entry = entry
            self._nodes = nodes
            self._edges = conditional_edges

        def invoke(self, state: "AssistantState") -> Dict[str, Any]:
            current = self._entry
            while True:
                node = self._nodes[current]
                state = {**state, **node(state)}

                router_and_edges = self._edges.get(current)
                if not router_and_edges:
                    return state

                router, edges = router_and_edges
                next_node = edges.get(router(state))
                if next_node is None or next_node == END:
                    return state
                current = next_node

    class StateGraph:
        def __init__(self, _state_type: type) -> None:
            self._nodes: Dict[str, Callable[["AssistantState"], Dict[str, Any]]] = {}
            self._edges: Dict[str, tuple[Callable[["AssistantState"], str], Dict[str, str]]] = {}
            self._entry: str | None = None

        def add_node(self, name: str, fn: Callable[["AssistantState"], Dict[str, Any]]):
            self._nodes[name] = fn

        def add_conditional_edges(
            self,
            from_node: str,
            router: Callable[["AssistantState"], str],
            edges: Dict[str, str],
        ) -> None:
            self._edges[from_node] = (router, edges)

        def add_edge(self, from_node: str, to_node: str) -> None:
            """Provide a minimal unconditional edge helper for parity with langgraph."""

            def _always(_state: "AssistantState") -> str:
                return "__next__"

            self._edges[from_node] = (_always, {"__next__": to_node})

        def set_entry_point(self, name: str):
            self._entry = name

        def compile(self) -> _CompiledGraph:
            if self._entry is None:
                raise ValueError("entry point not set")
            return _CompiledGraph(self._entry, self._nodes, self._edges)

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
