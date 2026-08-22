from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
AGENT_KIT = ROOT / "templates" / "agent-kit"
PATCHED_FLOORS = {
    "langchain-core": (1, 2, 22),
    "langgraph-checkpoint": (3, 0, 0),
    "orjson": (3, 11, 6),
    "urllib3": (2, 7, 0),
}


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def _locked_packages() -> dict[str, str]:
    lock = tomllib.loads((AGENT_KIT / "uv.lock").read_text(encoding="utf-8"))
    return {package["name"]: package["version"] for package in lock["package"]}


def test_agent_kit_declares_only_used_runtime_dependencies() -> None:
    document = tomllib.loads(
        (AGENT_KIT / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = document["project"]["dependencies"]
    constraints = document["tool"]["uv"]["constraint-dependencies"]

    assert dependencies == ["langgraph==1.2.10"]
    assert constraints == ["orjson>=3.11.6", "urllib3>=2.7.0"]
    assert not any(dependency.startswith("langchain") for dependency in dependencies)


def test_agent_kit_lock_excludes_all_known_high_severity_ranges() -> None:
    locked = _locked_packages()

    for package_name, patched_floor in PATCHED_FLOORS.items():
        assert package_name in locked
        assert _version_tuple(locked[package_name]) >= patched_floor

    assert "langchain" not in locked
