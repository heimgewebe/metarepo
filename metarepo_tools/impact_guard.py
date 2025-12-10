"""Impact guard utilities for contract change analysis."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path
    yaml = None  # type: ignore[assignment]


@dataclass
class ContractMeta:
    path: Path
    contract_id: str
    title: str
    producers: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)


def _parse_scalar(value: str):
    if value == "":
        return ""
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none", "~"}:
        return None
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _load_manifest_fallback(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, object]] = [(-1, root)]

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        content = line.strip()

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("List item without list parent in manifest")
            item_content = content[2:].strip()
            if not item_content:
                new_item: dict = {}
                parent.append(new_item)
                stack.append((indent, new_item))
                continue
            if ":" in item_content:
                key, value = item_content.split(":", 1)
                key = key.strip()
                value = value.strip()
                new_item = {key: _parse_scalar(value)}
                parent.append(new_item)
                stack.append((indent, new_item))
                if value == "":
                    new_dict: dict = {}
                    new_item[key] = new_dict
                    stack.append((indent + 2, new_dict))
            else:
                parent.append(_parse_scalar(item_content))
            continue

        if ":" in content:
            key, value = content.split(":", 1)
            key = key.strip()
            value = value.strip()
            if isinstance(parent, list):
                raise ValueError("Mapping entry encountered inside list without item")
            if value == "":
                if key in {"repos", "depends_on"}:
                    new_container: object = []
                else:
                    new_container = {}
                parent[key] = new_container
                stack.append((indent, new_container))
            else:
                parent[key] = _parse_scalar(value)
            continue

        raise ValueError(f"Unsupported manifest line: {raw_line}")

    return root


def load_manifest(manifest_path: Path) -> dict[str, dict]:
    text = manifest_path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = _load_manifest_fallback(text)
    repos: dict[str, dict] = {}
    for entry in data.get("repos", []):
        name = entry.get("name")
        if not name:
            continue
        repos[name] = entry
    return repos


def load_contracts(contracts_dir: Path) -> dict[str, ContractMeta]:
    contracts: dict[str, ContractMeta] = {}
    for path in sorted(contracts_dir.glob("*.schema.json")):
        rel = path.as_posix()
        payload = json.loads(path.read_text(encoding="utf-8"))
        contract_id = payload.get("$id", rel)
        title = payload.get("title", path.stem)
        producers = list(payload.get("x-producers", []))
        consumers = list(payload.get("x-consumers", []))
        contracts[rel] = ContractMeta(
            path=path,
            contract_id=contract_id,
            title=title,
            producers=producers,
            consumers=consumers,
        )
    return contracts


def sanitize_node(name: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]", "_", name)


def build_mermaid(
    contracts: Mapping[str, ContractMeta],
    manifest: Mapping[str, Mapping],
) -> str:
    lines: list[str] = ["graph LR"]
    seen_nodes: set[str] = set()

    def add_repo_node(repo: str) -> str:
        node_id = f"repo_{sanitize_node(repo)}"
        if node_id not in seen_nodes:
            info = manifest.get(repo, {})
            domain = info.get("domain", "")
            scope = info.get("scope", "")
            subtitle = ""
            if domain or scope:
                subtitle_text = f"{domain}:{scope}".strip(":")
                subtitle = f"<br/>{subtitle_text}" if subtitle_text else ""
            label = f"{repo}{subtitle}"
            lines.append(f'{node_id}["{label}"]')
            seen_nodes.add(node_id)
        return node_id

    def add_contract_node(contract: ContractMeta) -> str:
        node_id = f"contract_{sanitize_node(contract.path.stem)}"
        if node_id not in seen_nodes:
            label_name = (contract.path.name or "").replace('"', '\\"')
            label_title = (contract.title or "").replace('"', '\\"')
            lines.append(
                f'{node_id}{{"{label_name}\\n{label_title}"}}'
            )
            seen_nodes.add(node_id)
        return node_id

    for contract in contracts.values():
        contract_node = add_contract_node(contract)
        for repo in contract.producers:
            repo_node = add_repo_node(repo)
            lines.append(f"{repo_node} -->|produces| {contract_node}")
        for repo in contract.consumers:
            repo_node = add_repo_node(repo)
            lines.append(f"{contract_node} -->|consumes| {repo_node}")

    return "\n".join(lines)


def compute_dependents(manifest: Mapping[str, Mapping]) -> dict[str, list[str]]:
    dependents: dict[str, list[str]] = defaultdict(list)
    for repo, info in manifest.items():
        for dep in info.get("depends_on", []) or []:
            dependents[dep].append(repo)
    return dependents


def build_report(
    changed: Iterable[str],
    contracts: Mapping[str, ContractMeta],
    manifest: Mapping[str, Mapping],
) -> dict:
    changed_set = set(changed)
    dependents = compute_dependents(manifest)

    impacted_contracts = [contracts[c] for c in contracts if c in changed_set]

    repo_details: dict[str, dict] = {}

    for contract in impacted_contracts:
        for repo in contract.producers:
            info = repo_details.setdefault(repo, {
                "roles": set(),
                "contracts": [],
            })
            info["roles"].add("producer")
            info["contracts"].append(contract.path.as_posix())
        for repo in contract.consumers:
            info = repo_details.setdefault(repo, {
                "roles": set(),
                "contracts": [],
            })
            info["roles"].add("consumer")
            info["contracts"].append(contract.path.as_posix())

    for repo, info in list(repo_details.items()):
        meta = manifest.get(repo, {})
        info["roles"] = sorted(info["roles"])
        info["domain"] = meta.get("domain")
        info["scope"] = meta.get("scope")
        info["depends_on"] = meta.get("depends_on", []) or []
        info["dependents"] = dependents.get(repo, [])

    return {
        "changed_contracts": [c.path.as_posix() for c in impacted_contracts],
        "impacted_repos": repo_details,
    }


def write_markdown_report(
    report_path: Path,
    summary: Mapping,
    contracts: Mapping[str, ContractMeta],
    mermaid: str,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Impact Guard Report", ""]

    changed = summary.get("changed_contracts", [])
    if changed:
        lines.append("## Changed Contracts")
        for contract_path in changed:
            contract = contracts.get(contract_path)
            title = contract.title if contract else contract_path
            lines.append(f"- `{contract_path}` — {title}")
        lines.append("")
    else:
        lines.append("No contract changes detected.")
        lines.append("")

    impacted = summary.get("impacted_repos", {})
    if impacted:
        lines.append("## Impacted Repositories")
        lines.append("| Repo | Roles | Domain | Scope | Depends on | Dependents |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for repo, info in sorted(impacted.items()):
            roles = ", ".join(info.get("roles", [])) or "-"
            domain = info.get("domain") or "-"
            scope = info.get("scope") or "-"
            depends_on = ", ".join(info.get("depends_on", [])) or "-"
            dependents = ", ".join(info.get("dependents", [])) or "-"
            lines.append(
                f"| {repo} | {roles} | {domain} | {scope} | {depends_on} | {dependents} |"
            )
        lines.append("")

    if mermaid:
        lines.append("## Fleet Contract Graph")
        lines.append("```mermaid")
        lines.append(mermaid)
        lines.append("```")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Impact guard contract analyzer")
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path("contracts"),
        help="Directory containing contract schemas",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("repos.yml"),
        help="Fleet manifest with repo metadata",
    )
    parser.add_argument(
        "--graph-out",
        type=Path,
        default=Path("reports/impact/impact-graph.mmd"),
        help="Path to write the Mermaid graph",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("reports/impact/impact-report.md"),
        help="Path to write the Markdown summary",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("reports/impact/impact-report.json"),
        help="Path to write the machine-readable summary",
    )
    parser.add_argument(
        "changed",
        nargs="*",
        help="List of changed contract paths (relative to repo root)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contracts = load_contracts(args.contracts_dir)
    manifest = load_manifest(args.manifest)

    changed = [c for c in args.changed if c in contracts]
    summary = build_report(changed, contracts, manifest)

    mermaid = build_mermaid(contracts, manifest)

    args.graph_out.parent.mkdir(parents=True, exist_ok=True)
    args.graph_out.write_text(mermaid + "\n", encoding="utf-8")

    write_markdown_report(args.report_out, summary, contracts, mermaid)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if summary.get("impacted_repos"):
        print("::notice::Impact guard detected affected repositories.")
    else:
        print("::notice::No repositories affected by the provided changes.")


if __name__ == "__main__":
    main()
