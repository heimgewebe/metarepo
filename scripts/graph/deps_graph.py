#!/usr/bin/env python3
"""Build a dependency graph for the heimgewebe metarepo ecosystem."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, MutableSet, Sequence

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore

import networkx as nx
import yaml

RepoName = str


@dataclass(frozen=True)
class Repo:
    """Metadata about a heimgewebe repository."""

    name: RepoName
    path: Path | None
    metadata: Mapping[str, object]
    declared_dependencies: Sequence[RepoName]

    @property
    def exists_locally(self) -> bool:
        return self.path is not None and self.path.exists()


def normalize(name: str) -> str:
    """Normalise dependency identifiers to compare with repo names."""

    return name.lower().replace("-", "").replace("_", "")


def _coerce_metadata(value: object) -> object:
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True)
    return value


def load_repos(manifest_path: Path) -> Dict[RepoName, Repo]:
    """Load repository metadata from repos.yml."""

    if not manifest_path.exists():
        print(
            f"WARNING: Repository manifest not found at {manifest_path} – generated graph will be empty.",
            file=sys.stderr,
        )
        return {}

    data = yaml.safe_load(manifest_path.read_text())
    repos: Dict[RepoName, Repo] = {}
    repo_entries = data.get("repos", []) if isinstance(data, Mapping) else []

    for entry in repo_entries:
        if not isinstance(entry, Mapping):
            continue
        name = str(entry.get("name"))
        repo_path = resolve_repo_path(name)
        depends_on = entry.get("depends_on", [])
        deps: List[str] = []
        if isinstance(depends_on, Sequence):
            for dep in depends_on:
                if isinstance(dep, str):
                    deps.append(dep)
        repos[name] = Repo(
            name=name,
            path=repo_path,
            metadata={
                k: _coerce_metadata(v) for k, v in entry.items() if k not in {"name", "depends_on"}
            },
            declared_dependencies=tuple(deps),
        )
    return repos


def resolve_repo_path(name: str, candidate_roots: Sequence[Path] | None = None) -> Path | None:
    """Resolve a repository name to a local checkout path if available."""

    if candidate_roots is None:
        candidate_roots = (
            Path("repos"),
            Path(".."),
            Path("../repos"),
        )

    normalized = {name, name.lower(), normalize(name)}

    for root in candidate_roots:
        for candidate_name in normalized:
            candidate = root / candidate_name
            if candidate.exists():
                return candidate.resolve()
    return None


def iter_dependency_files(repo: Repo) -> Iterator[Path]:
    """Iterate over dependency declaration files within a repository."""

    if not repo.exists_locally:
        return

    patterns = ("Cargo.toml", "pyproject.toml", "package.json", "requirements.txt")
    repo_path = repo.path
    assert repo_path is not None
    for root, _, files in os.walk(repo_path):
        for filename in files:
            if filename in patterns or filename.startswith("requirements") and filename.endswith(".txt"):
                yield Path(root) / filename


def parse_dependencies(path: Path) -> Iterable[str]:
    """Parse dependency identifiers from the supported file types."""

    name = path.name
    try:
        if name == "Cargo.toml":
            return _parse_cargo_dependencies(path)
        if name == "package.json":
            return _parse_package_dependencies(path)
        if name == "pyproject.toml":
            return _parse_pyproject_dependencies(path)
        if name.endswith(".txt") and name.startswith("requirements"):
            return _parse_requirements_dependencies(path)
    except (OSError, ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:  # pragma: no cover - defensive logging
        print(f"WARNING: Failed to parse {path}: {exc}")
    except Exception as exc:  # pragma: no cover - catch tomllib.TOMLDecodeError and tomli.TOMLDecodeError
        if "TOMLDecodeError" in type(exc).__name__:
            print(f"WARNING: Failed to parse {path}: {exc}")
        else:
            raise
    return ()


def _parse_cargo_dependencies(path: Path) -> Iterable[str]:
    data = tomllib.loads(path.read_text())
    results: MutableSet[str] = set()
    sections = [
        "dependencies",
        "dev-dependencies",
        "build-dependencies",
    ]
    for section in sections:
        section_data = data.get(section, {})
        if isinstance(section_data, Mapping):
            results.update(str(key) for key in section_data.keys())
    workspace = data.get("workspace", {})
    if isinstance(workspace, Mapping):
        workspace_deps = workspace.get("dependencies", {})
        if isinstance(workspace_deps, Mapping):
            results.update(str(key) for key in workspace_deps.keys())
    return results


def _parse_package_dependencies(path: Path) -> Iterable[str]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    results: MutableSet[str] = set()
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section_data = data.get(section, {})
        if isinstance(section_data, Mapping):
            results.update(str(key) for key in section_data.keys())
    return results


def _parse_pyproject_dependencies(path: Path) -> Iterable[str]:
    data = tomllib.loads(path.read_text())
    results: MutableSet[str] = set()

    def _consume(seq: object) -> None:
        if isinstance(seq, Sequence):
            for item in seq:
                if isinstance(item, str):
                    results.add(_strip_extras(item))

    project = data.get("project", {})
    if isinstance(project, Mapping):
        _consume(project.get("dependencies"))
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, Mapping):
            for deps in optional.values():
                _consume(deps)

    tool = data.get("tool", {})
    if isinstance(tool, Mapping):
        poetry = tool.get("poetry", {})
        if isinstance(poetry, Mapping):
            deps = poetry.get("dependencies")
            if isinstance(deps, Mapping):
                results.update(str(key) for key in deps.keys())
            dev = poetry.get("dev-dependencies")
            if isinstance(dev, Mapping):
                results.update(str(key) for key in dev.keys())
    return results


def _strip_extras(dependency: str) -> str:
    token = dependency.split(";")[0]
    token = token.split("[")[0]
    token = token.split("(")[0]
    return token.strip()


def _parse_requirements_dependencies(path: Path) -> Iterable[str]:
    results: MutableSet[str] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        token = _strip_extras(line)
        if token:
            results.add(token)
    return results


def build_graph(
    repos: Mapping[RepoName, Repo],
    *,
    repo_lookup: Mapping[str, RepoName],
) -> nx.DiGraph:
    """Create the dependency graph using declared and inferred dependencies."""

    graph = nx.DiGraph()

    for repo in repos.values():
        graph.add_node(repo.name, **repo.metadata)

    for repo in repos.values():
        for declared in repo.declared_dependencies:
            if declared in repos:
                _add_edge(graph, repo.name, declared, "manifest")

        if not repo.exists_locally:
            continue

        for dep_file in iter_dependency_files(repo):
            inferred = set()
            for dependency in parse_dependencies(dep_file):
                normalized = normalize(dependency)
                target = repo_lookup.get(normalized)
                if target and target != repo.name:
                    inferred.add(target)
            for target in sorted(inferred):
                _add_edge(graph, repo.name, target, f"file:{dep_file.relative_to(repo.path)}")
    return graph


def _add_edge(graph: nx.DiGraph, source: RepoName, target: RepoName, origin: str) -> None:
    data = graph.get_edge_data(source, target)
    if data is None:
        graph.add_edge(source, target, sources=[origin])
    else:
        sources = data.setdefault("sources", [])
        if origin not in sources:
            sources.append(origin)


def write_outputs(graph: nx.DiGraph, gexf_path: Path, json_path: Path | None = None) -> None:
    copy = graph.copy()
    for _, _, data in copy.edges(data=True):
        if "sources" in data:
            data["sources"] = ";".join(sorted(data["sources"]))
    nx.write_gexf(copy, gexf_path)
    if json_path:
        with json_path.open("w", encoding="utf-8") as fp:
            json.dump(nx.readwrite.json_graph.node_link_data(graph), fp, indent=2, sort_keys=True)


def prepare_lookup(repos: Mapping[RepoName, Repo]) -> Dict[str, RepoName]:
    lookup: Dict[str, RepoName] = {}
    for repo in repos.values():
        variants = {repo.name, repo.name.lower(), normalize(repo.name)}
        for variant in variants:
            lookup.setdefault(variant, repo.name)
    return lookup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="repos.yml", type=Path, help="Path to repos.yml")
    parser.add_argument(
        "--output",
        default=Path("deps_graph.gexf"),
        type=Path,
        help="Path where the GEXF graph should be written.",
    )
    parser.add_argument(
        "--json-output",
        default=None,
        type=Path,
        help="Optional path for a JSON node-link export.",
    )
    parser.add_argument(
        "--repos-root",
        default=None,
        type=Path,
        help="Override repository root discovery (defaults to ../<name>).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.repos_root:
        candidate_roots = (args.repos_root,)
    else:
        candidate_roots = None

    repos = load_repos(args.manifest)
    if candidate_roots is not None:
        override = {}
        for name in repos:
            override[name] = resolve_repo_path(name, candidate_roots)
        repos = {
            name: Repo(
                name=name,
                path=override[name],
                metadata=repo.metadata,
                declared_dependencies=repo.declared_dependencies,
            )
            for name, repo in repos.items()
        }

    lookup = prepare_lookup(repos)
    graph = build_graph(repos, repo_lookup=lookup)
    write_outputs(graph, args.output, args.json_output)
    print(
        f"Wrote dependency graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges to {args.output}."
    )


if __name__ == "__main__":
    main()
