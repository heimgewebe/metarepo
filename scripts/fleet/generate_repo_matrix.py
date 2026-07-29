#!/usr/bin/env python3
"""Generate the human-readable Fleet matrix from canonical Fleet sources."""
from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wgx import repo_config

DEFAULT_FLEET = ROOT / "fleet" / "repos.yml"
DEFAULT_METADATA = ROOT / "fleet" / "repo-metadata.yml"
DEFAULT_OUTPUT = ROOT / "docs" / "repo-matrix.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metadata(path: Path) -> dict[str, dict[str, Any]]:
    data = repo_config.load_config(path)
    repositories = data.get("repositories", {})
    if not isinstance(repositories, dict):
        raise ValueError("fleet/repo-metadata.yml repositories must be a mapping")
    result: dict[str, dict[str, Any]] = {}
    for name, value in repositories.items():
        if isinstance(name, str) and isinstance(value, dict):
            result[name] = value
    return result


def _role(name: str, metadata: dict[str, dict[str, Any]]) -> str:
    config = metadata.get(name, {})
    domain = config.get("domain")
    scope = config.get("scope")
    if isinstance(domain, str) and isinstance(scope, str):
        return f"{domain} / {scope}"
    return "Aktives Fleet-Mitglied"


def _reference_role(entry: dict[str, Any]) -> str:
    status = entry.get("status", "related")
    if status == "historical-donor":
        return "Historischer Spender; keine aktive Produkt-, Fleet- oder Runtime-Autorität"
    if status == "archived-reference":
        return "Archivierte Referenz; keine aktive Betriebs- oder Entwicklungsautorität"
    return "Zugehörige Non-Fleet-Referenz"


def _table(rows: list[tuple[str, str, str]]) -> list[str]:
    lines = ["| Repo | Rolle | Fleet |", "| --- | --- | --- |"]
    lines.extend(f"| {name} | {role} | {fleet} |" for name, role, fleet in rows)
    return lines


def render(fleet_path: Path, metadata_path: Path) -> str:
    fleet = repo_config.load_config(fleet_path)
    metadata = _metadata(metadata_path)
    active = repo_config.active_fleet_repos(fleet)

    static = fleet.get("static", {}) or {}
    includes = static.get("include", []) if isinstance(static, dict) else []
    if not isinstance(includes, list):
        raise ValueError("fleet static.include must be a list")

    donors: list[tuple[str, str, str]] = []
    archived: list[tuple[str, str, str]] = []
    related: list[tuple[str, str, str]] = []
    for raw in includes:
        entry = repo_config.to_repo_object(raw)
        if entry.get("fleet") is not False:
            continue
        row = (str(entry["name"]), _reference_role(entry), "no")
        status = entry.get("status")
        if status == "historical-donor":
            donors.append(row)
        elif status == "archived-reference":
            archived.append(row)
        else:
            related.append(row)

    lines = [
        "# Repo-Matrix",
        "",
        "<!-- GENERATED FILE - DO NOT EDIT -->",
        "<!-- Canonical source: fleet/repos.yml -->",
        f"<!-- Fleet SHA-256: {_sha256(fleet_path)} -->",
        f"<!-- Metadata SHA-256: {_sha256(metadata_path)} -->",
        "",
        "Diese Matrix ist eine menschenlesbare Projektion. Die normative Fleet-Mitgliedschaft liegt ausschließlich in `fleet/repos.yml`; operative Zusatzdaten liegen in `fleet/repo-metadata.yml`.",
        "",
        "## Aktive Fleet",
        "",
        *_table([(entry["name"], _role(entry["name"], metadata), "yes") for entry in active]),
        "",
        "## Historische Spender (Non-Fleet)",
        "",
        *(_table(donors) if donors else ["_Keine._"]),
        "",
        "## Archivierte Referenzen (Non-Fleet)",
        "",
        *(_table(archived) if archived else ["_Keine._"]),
        "",
        "## Weitere Referenzen (Non-Fleet)",
        "",
        *(_table(related) if related else ["_Keine._"]),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fleet-file", type=Path, default=DEFAULT_FLEET)
    parser.add_argument("--metadata-file", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = render(args.fleet_file, args.metadata_file)
    if args.check:
        actual = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if actual == expected:
            print("repo matrix projection: PASS")
            return 0
        sys.stdout.writelines(difflib.unified_diff(
            actual.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=str(args.output),
            tofile="generated",
        ))
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
