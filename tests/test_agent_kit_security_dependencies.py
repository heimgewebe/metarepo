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


def _agent_kit_pyproject() -> dict[str, object]:
    return tomllib.loads((AGENT_KIT / "pyproject.toml").read_text(encoding="utf-8"))


def _locked_packages() -> dict[str, str]:
    lock = tomllib.loads((AGENT_KIT / "uv.lock").read_text(encoding="utf-8"))
    return {package["name"]: package["version"] for package in lock["package"]}


def _exact_langgraph_pin(document: dict[str, object]) -> str:
    project = document["project"]
    assert isinstance(project, dict)
    dependencies = project["dependencies"]
    assert isinstance(dependencies, list)
    assert len(dependencies) == 1

    requirement = dependencies[0]
    assert isinstance(requirement, str)
    prefix = "langgraph=="
    assert requirement.startswith(prefix)

    version = requirement.removeprefix(prefix)
    assert version and _version_tuple(version)
    return version


def test_agent_kit_declares_only_used_runtime_dependencies() -> None:
    document = _agent_kit_pyproject()
    project = document["project"]
    tool = document["tool"]
    assert isinstance(project, dict)
    assert isinstance(tool, dict)
    uv = tool["uv"]
    assert isinstance(uv, dict)

    dependencies = project["dependencies"]
    constraints = uv["constraint-dependencies"]
    langgraph_version = _exact_langgraph_pin(document)

    assert _locked_packages()["langgraph"] == langgraph_version
    assert constraints == ["orjson>=3.11.6", "urllib3>=2.7.0"]
    assert not any(dependency.startswith("langchain") for dependency in dependencies)


def test_agent_kit_lock_excludes_all_known_high_severity_ranges() -> None:
    locked = _locked_packages()

    for package_name, patched_floor in PATCHED_FLOORS.items():
        assert package_name in locked
        assert _version_tuple(locked[package_name]) >= patched_floor

    assert "langchain" not in locked
