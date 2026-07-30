from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_KIT = ROOT / "templates" / "agent-kit"
PATCHED_LANGCHAIN_CORE = (0, 3, 81)


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def _locked_version(package_name: str) -> str:
    lock = tomllib.loads((AGENT_KIT / "uv.lock").read_text(encoding="utf-8"))
    matches = [
        package["version"]
        for package in lock["package"]
        if package["name"] == package_name
    ]
    assert len(matches) == 1
    return matches[0]


def test_agent_kit_declares_patched_langchain_core_floor() -> None:
    project = tomllib.loads(
        (AGENT_KIT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    assert "langchain==0.3.30" in project["dependencies"]
    assert "langchain-core>=0.3.81,<0.4.0" in project["dependencies"]


def test_agent_kit_lock_excludes_critical_langchain_core_range() -> None:
    locked = _version_tuple(_locked_version("langchain-core"))

    assert PATCHED_LANGCHAIN_CORE <= locked < (0, 4, 0)
