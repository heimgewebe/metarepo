from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_LOCK = ROOT / "contracts" / "package-lock.json"
LOCAL_MCP_NPM_LOCK = ROOT / "servers" / "local-mcp" / "package-lock.json"
LOCAL_MCP_PNPM_LOCK = ROOT / "servers" / "local-mcp" / "pnpm-lock.yaml"

CONTRACTS_PATCHED_FLOORS = {
    "brace-expansion": (1, 1, 16),
    "fast-uri": (3, 1, 4),
    "js-yaml": (3, 15, 0),
}
LOCAL_MCP_PATCHED_FLOORS = {
    "fast-uri": (3, 1, 4),
    "hono": (4, 12, 25),
    "path-to-regexp": (8, 4, 0),
}


def _version_tuple(value: str) -> tuple[int, int, int]:
    major, minor, patch = value.split(".", maxsplit=2)
    return int(major), int(minor), int(patch)


def _npm_versions(lock_path: Path, package_name: str) -> set[str]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    suffix = f"node_modules/{package_name}"
    return {
        package["version"]
        for path, package in lock["packages"].items()
        if path == suffix or path.endswith(f"/{suffix}")
    }


def _pnpm_versions(lock_path: Path, package_name: str) -> set[str]:
    text = lock_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^  '?{re.escape(package_name)}@(\d+\.\d+\.\d+)'?:$",
        re.MULTILINE,
    )
    return set(pattern.findall(text))


def _assert_patched_versions(
    lock_path: Path,
    floors: dict[str, tuple[int, int, int]],
) -> None:
    for package_name, patched_floor in floors.items():
        versions = _npm_versions(lock_path, package_name)
        assert versions, f"{package_name} missing from {lock_path}"
        assert all(_version_tuple(version) >= patched_floor for version in versions), (
            package_name,
            versions,
            patched_floor,
        )


def test_contracts_lock_excludes_selected_high_severity_ranges() -> None:
    _assert_patched_versions(CONTRACTS_LOCK, CONTRACTS_PATCHED_FLOORS)


def test_local_mcp_npm_lock_excludes_selected_high_severity_ranges() -> None:
    _assert_patched_versions(LOCAL_MCP_NPM_LOCK, LOCAL_MCP_PATCHED_FLOORS)


def test_local_mcp_npm_and_pnpm_locks_resolve_same_security_versions() -> None:
    for package_name, patched_floor in LOCAL_MCP_PATCHED_FLOORS.items():
        npm_versions = _npm_versions(LOCAL_MCP_NPM_LOCK, package_name)
        pnpm_versions = _pnpm_versions(LOCAL_MCP_PNPM_LOCK, package_name)

        assert pnpm_versions, f"{package_name} missing from {LOCAL_MCP_PNPM_LOCK}"
        assert npm_versions == pnpm_versions
        assert all(_version_tuple(version) >= patched_floor for version in pnpm_versions)


def test_local_mcp_locks_preserve_node_18_server_compatibility() -> None:
    package_name = "@hono/node-server"
    npm_versions = _npm_versions(LOCAL_MCP_NPM_LOCK, package_name)
    pnpm_versions = _pnpm_versions(LOCAL_MCP_PNPM_LOCK, package_name)

    assert npm_versions == pnpm_versions
    assert npm_versions
    assert all(_version_tuple(version) < (2, 0, 0) for version in npm_versions)
