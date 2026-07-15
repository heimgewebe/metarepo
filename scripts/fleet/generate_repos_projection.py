#!/usr/bin/env python3
"""Generate the legacy top-level repos.yml compatibility projection.

Canonical inputs:
  * fleet/repos.yml          -- Fleet membership and related repositories
  * fleet/repo-metadata.yml  -- operational metadata for legacy consumers

The generated top-level repos.yml is intentionally non-authoritative. Existing
WGX, graph and template tooling may continue to read it until those consumers
are migrated, but CI requires byte-for-byte reproducibility from the canonical
inputs.
"""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FLEET = ROOT / "fleet" / "repos.yml"
DEFAULT_METADATA = ROOT / "fleet" / "repo-metadata.yml"
DEFAULT_OUTPUT = ROOT / "repos.yml"
HEADER = (
    "# GENERATED FILE. DO NOT EDIT.\n"
    "# Sources: fleet/repos.yml and fleet/repo-metadata.yml\n"
)
REPO_FIELD_ORDER = (
    "url",
    "default_branch",
    "depends_on",
    "domain",
    "scope",
    "metrics",
    "wgx",
    "integrity",
)
ALLOWED_REPO_FIELDS = set(REPO_FIELD_ORDER)
MAPPING_REPO_FIELDS = ("metrics", "wgx", "integrity")
STRING_REPO_FIELDS = ("domain", "scope")


class ProjectionError(ValueError):
    """Raised when canonical Fleet inputs cannot produce a safe projection."""


class IndentedSafeDumper(yaml.SafeDumper):
    """Safe dumper that preserves legacy-compatible sequence indentation."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_mapping(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except FileNotFoundError as exc:
        raise ProjectionError(f"{label} not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ProjectionError(f"{label} is not valid unique-key YAML: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectionError(f"{label} must have a mapping root: {path}")
    return value


def _entry_name(entry: Any, *, label: str) -> str:
    if isinstance(entry, str) and entry.strip():
        return entry.strip()
    if isinstance(entry, dict):
        name = entry.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    raise ProjectionError(f"{label} entry must contain a non-empty name")


def _static_entry_is_projectable(entry: Any, *, label: str) -> bool:
    if not isinstance(entry, dict) or "fleet" not in entry:
        return True
    fleet_flag = entry["fleet"]
    if not isinstance(fleet_flag, bool):
        raise ProjectionError(f"{label}.fleet must be boolean when present")
    return fleet_flag


def collect_projectable_repositories(fleet: dict[str, Any]) -> set[str]:
    """Return repositories eligible for the public compatibility projection."""

    all_names: set[str] = set()
    projectable: set[str] = set()

    repos = fleet.get("repos")
    if not isinstance(repos, list):
        raise ProjectionError("fleet/repos.yml must contain a repos list")
    for index, entry in enumerate(repos):
        name = _entry_name(entry, label=f"repos[{index}]")
        if name in all_names:
            raise ProjectionError(f"duplicate Fleet repository: {name}")
        all_names.add(name)
        projectable.add(name)

    static = fleet.get("static", {})
    if static is None:
        static = {}
    if not isinstance(static, dict):
        raise ProjectionError("fleet/repos.yml static must be a mapping")
    include = static.get("include", [])
    if include is None:
        include = []
    if not isinstance(include, list):
        raise ProjectionError("fleet/repos.yml static.include must be a list")
    for index, entry in enumerate(include):
        label = f"static.include[{index}]"
        name = _entry_name(entry, label=label)
        if name in all_names:
            raise ProjectionError(f"repository occurs more than once in Fleet scope: {name}")
        all_names.add(name)
        if _static_entry_is_projectable(entry, label=label):
            projectable.add(name)

    if not projectable:
        raise ProjectionError("fleet/repos.yml contains no projectable repositories")
    return projectable


def _validated_metadata_config(
    name: str,
    raw_config: Any,
    *,
    owner: str,
    projectable: set[str],
) -> dict[str, Any]:
    if not isinstance(raw_config, dict):
        raise ProjectionError(f"metadata for {name} must be a mapping")

    unknown_fields = sorted(set(raw_config) - ALLOWED_REPO_FIELDS)
    if unknown_fields:
        raise ProjectionError(
            f"unsupported metadata fields for {name}: {', '.join(unknown_fields)}"
        )

    default_branch = raw_config.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch.strip():
        raise ProjectionError(f"{name}.default_branch must be non-empty")

    raw_dependencies = raw_config.get("depends_on", [])
    if not isinstance(raw_dependencies, list) or not all(
        isinstance(value, str) and value.strip() for value in raw_dependencies
    ):
        raise ProjectionError(f"{name}.depends_on must be a list of names")
    dependencies = [value.strip() for value in raw_dependencies]
    if len(dependencies) != len(set(dependencies)):
        raise ProjectionError(f"{name}.depends_on contains duplicates")
    unknown_dependencies = sorted(set(dependencies) - projectable)
    if unknown_dependencies:
        raise ProjectionError(
            f"{name}.depends_on references non-projectable repositories: "
            + ", ".join(unknown_dependencies)
        )

    raw_url = raw_config.get("url")
    if raw_url is None:
        url = f"https://github.com/{owner}/{name}"
    elif isinstance(raw_url, str) and raw_url.strip():
        url = raw_url.strip()
    else:
        raise ProjectionError(f"{name}.url must be a non-empty string")

    for field in STRING_REPO_FIELDS:
        value = raw_config.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ProjectionError(f"{name}.{field} must be a non-empty string")

    for field in MAPPING_REPO_FIELDS:
        value = raw_config.get(field)
        if value is not None and not isinstance(value, dict):
            raise ProjectionError(f"{name}.{field} must be a mapping")

    normalized: dict[str, Any] = {"url": url, "default_branch": default_branch.strip()}
    if dependencies:
        normalized["depends_on"] = dependencies
    for field in STRING_REPO_FIELDS:
        if field in raw_config:
            normalized[field] = raw_config[field].strip()
    for field in MAPPING_REPO_FIELDS:
        if field in raw_config:
            normalized[field] = raw_config[field]
    return normalized


def build_projection(
    fleet: dict[str, Any], metadata: dict[str, Any]
) -> dict[str, Any]:
    if metadata.get("schema_version") != 1:
        raise ProjectionError("fleet/repo-metadata.yml schema_version must be 1")

    github = metadata.get("github")
    if not isinstance(github, dict):
        raise ProjectionError("fleet/repo-metadata.yml github must be a mapping")
    owner = github.get("owner")
    if not isinstance(owner, str) or not owner.strip():
        raise ProjectionError("fleet/repo-metadata.yml github.owner must be non-empty")
    owner = owner.strip()

    repositories = metadata.get("repositories")
    if not isinstance(repositories, dict) or not repositories:
        raise ProjectionError(
            "fleet/repo-metadata.yml repositories must be a non-empty mapping"
        )

    projectable = collect_projectable_repositories(fleet)
    projected: list[dict[str, Any]] = []
    normalized_names: set[str] = set()

    for raw_name, raw_config in repositories.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ProjectionError("repository metadata keys must be non-empty strings")
        name = raw_name.strip()
        if name in normalized_names:
            raise ProjectionError(f"duplicate normalized metadata repository: {name}")
        normalized_names.add(name)
        if name not in projectable:
            raise ProjectionError(
                f"metadata repository is not projectable from fleet/repos.yml: {name}"
            )

        config = _validated_metadata_config(
            name,
            raw_config,
            owner=owner,
            projectable=projectable,
        )
        entry: dict[str, Any] = {"name": name}
        for field in REPO_FIELD_ORDER:
            if field in config:
                entry[field] = config[field]
        projected.append(entry)

    return {
        "mode": "static",
        "github": {"owner": owner},
        "repos": projected,
    }


def render_projection(projection: dict[str, Any]) -> str:
    body = yaml.dump(
        projection,
        Dumper=IndentedSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1000,
    )
    return HEADER + body


def expected_projection(fleet_path: Path, metadata_path: Path) -> str:
    fleet = load_mapping(fleet_path, label="Fleet membership")
    metadata = load_mapping(metadata_path, label="Fleet metadata")
    return render_projection(build_projection(fleet, metadata))


def check_projection(output_path: Path, expected: str) -> bool:
    try:
        current = output_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"projection missing: {output_path}", file=sys.stderr)
        return False
    if current == expected:
        return True
    diff = difflib.unified_diff(
        current.splitlines(),
        expected.splitlines(),
        fromfile=str(output_path),
        tofile=f"generated:{output_path}",
        lineterm="",
    )
    print("repos.yml is stale; regenerate it from canonical Fleet inputs:", file=sys.stderr)
    print("\n".join(diff), file=sys.stderr)
    return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fleet-file", type=Path, default=DEFAULT_FLEET)
    parser.add_argument("--metadata-file", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless the output already equals the deterministic projection",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="print the projection instead of writing it",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.check and args.stdout:
        raise ProjectionError("--check and --stdout are mutually exclusive")

    expected = expected_projection(args.fleet_file, args.metadata_file)
    if args.check:
        return 0 if check_projection(args.output, expected) else 1
    if args.stdout:
        sys.stdout.write(expected)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"wrote generated compatibility projection: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProjectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
