#!/usr/bin/env python3
"""Analyse the impact of schema changes across heimgewebe repositories."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence, Set

import networkx as nx

from scripts.graph.deps_graph import (
    Repo,
    build_graph,
    load_repos,
    normalize,
    prepare_lookup,
    resolve_repo_path,
)


@dataclass(frozen=True)
class SchemaImpact:
    schema: str
    producers: Set[str]
    consumers: Set[str]

    def participants(self) -> Set[str]:
        return set(self.producers) | set(self.consumers)


def parse_contract_index(path: Path, repo_lookup: Mapping[str, str]) -> Dict[str, SchemaImpact]:
    """Parse docs/contracts/index.md to map schemas to producer/consumer repos."""

    import re

    impacts: Dict[str, SchemaImpact] = {}
    rows_started = False
    link_pattern = re.compile(r"\]\(([^)]+)\)")
    code_pattern = re.compile(r"`([^`]+)`")

    def _extract_repos(cell: str) -> Set[str]:
        names: Set[str] = set()
        for token in code_pattern.findall(cell):
            norm = normalize(token)
            target = repo_lookup.get(norm)
            if target:
                names.add(target)
        # fall back to comma separated tokens to catch plain names
        for token in cell.split(","):
            token = token.strip().strip("`").strip()
            if not token:
                continue
            norm = normalize(token)
            target = repo_lookup.get(norm)
            if target:
                names.add(target)
        return names

    if not path.exists():
        print(f"WARNING: Contracts index not found at {path} – no schema metadata loaded.", file=sys.stderr)
        return impacts

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("|"):
                if rows_started and line.strip() == "":
                    break
                continue
            row = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not rows_started:
                rows_started = True
                continue  # header row
            if row[0].startswith("---"):
                continue
            if len(row) < 4:
                continue
            schema_cell, _purpose, producer_cell, consumer_cell = row[:4]
            link_match = link_pattern.search(schema_cell)
            if not link_match:
                continue
            schema_path = link_match.group(1)
            if schema_path.startswith("../../"):
                schema_path = schema_path[6:]
            producers = _extract_repos(producer_cell)
            consumers = _extract_repos(consumer_cell)
            impacts[schema_path] = SchemaImpact(
                schema=schema_path,
                producers=producers,
                consumers=consumers,
            )
    return impacts


def gather_changed_schemas(args: argparse.Namespace) -> Set[str]:
    schemas: Set[str] = set()
    for item in args.schemas:
        schemas.update(_expand_schema_input(item))
    if args.changes_file:
        for line in args.changes_file.read_text().splitlines():
            schemas.update(_expand_schema_input(line))
    if not schemas:
        raise SystemExit("No schema paths supplied. Provide --changes-file or positional schema arguments.")
    return schemas


def _expand_schema_input(raw: str) -> Set[str]:
    raw = raw.strip()
    if not raw:
        return set()
    path = raw
    if raw.startswith("./"):
        path = raw[2:]
    if raw.startswith("../../"):
        path = raw[6:]
    path = path.lstrip("/")
    if path.startswith("contracts/"):
        return {path}
    if path.endswith(".json") and "contracts" in path:
        idx = path.find("contracts")
        return {path[idx:]}
    return set()


def load_dependency_graph(args: argparse.Namespace, repos: Mapping[str, Repo]) -> nx.DiGraph:
    if args.graph and Path(args.graph).exists():
        graph = nx.read_gexf(args.graph)
        return graph
    lookup = prepare_lookup(repos)
    return build_graph(repos, repo_lookup=lookup)


def impact_summary(
    graph: nx.DiGraph,
    impacts: Mapping[str, SchemaImpact],
    schemas: Iterable[str],
    *,
    include_transitive: bool,
) -> Dict[str, Dict[str, Sequence[str]]]:
    summary: Dict[str, Dict[str, Sequence[str]]] = {}
    for schema in schemas:
        impact = impacts.get(schema)
        if impact is None:
            continue
        direct = impact.participants()
        upstream: Set[str] = set()
        downstream: Set[str] = set()
        if include_transitive:
            for repo in direct:
                if repo in graph:
                    upstream.update(nx.ancestors(graph, repo))
                    downstream.update(nx.descendants(graph, repo))
        summary[schema] = {
            "producers": sorted(impact.producers),
            "consumers": sorted(impact.consumers),
            "direct": sorted(direct),
            "upstream": sorted(upstream - direct),
            "downstream": sorted(downstream - direct),
            "impact": sorted(direct | upstream | downstream),
        }
    return summary


def emit_text(summary: Mapping[str, Mapping[str, Sequence[str]]]) -> None:
    if not summary:
        print("No known schemas were matched.")
        return
    for schema, data in summary.items():
        print(f"Schema: {schema}")
        for key in ("producers", "consumers", "direct", "upstream", "downstream", "impact"):
            values = data.get(key, [])
            if values:
                print(f"  {key.capitalize()}: {', '.join(values)}")
            else:
                print(f"  {key.capitalize()}: –")
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schemas", nargs="*", help="Schema paths (e.g. contracts/audio.events.schema.json).")
    parser.add_argument(
        "--manifest",
        default=Path("repos.yml"),
        type=Path,
        help="Path to the repos.yml manifest used for dependency inference.",
    )
    parser.add_argument(
        "--contracts-index",
        default=Path("docs/contracts/index.md"),
        type=Path,
        help="Markdown table with schema producer/consumer mapping.",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        help="Optional path to a precomputed deps_graph.gexf. Rebuilt when missing.",
    )
    parser.add_argument(
        "--changes-file",
        type=Path,
        help="File containing newline separated changed paths (e.g. output of git diff --name-only).",
    )
    parser.add_argument(
        "--repos-root",
        type=Path,
        help="Override the root directory when resolving local repo clones.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON file to persist the impact summary.",
    )
    parser.add_argument(
        "--no-transitive",
        action="store_true",
        help="Only list direct producers/consumers without traversing the dependency graph.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render output as human readable text or JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repos = load_repos(args.manifest)
    if args.repos_root:
        override = {}
        for name in repos:
            override[name] = resolve_repo_path(name, (args.repos_root,))
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
    graph = load_dependency_graph(args, repos)
    impacts = parse_contract_index(args.contracts_index, lookup)
    schemas = gather_changed_schemas(args)
    summary = impact_summary(graph, impacts, schemas, include_transitive=not args.no_transitive)

    if args.format == "json":
        output = json.dumps(summary, indent=2, sort_keys=True)
        print(output)
    else:
        emit_text(summary)

    if args.json_output:
        args.json_output.write_text(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
