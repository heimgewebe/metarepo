from __future__ import annotations
from typing import TypedDict, List, Dict, Any


class AssistantState(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    current_task: str
    code_context: Dict[str, Any]
    knowledge_hits: List[Dict[str, Any]]
    result: Dict[str, Any]
    next: str
