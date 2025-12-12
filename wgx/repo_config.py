#!/usr/bin/env python3
"""Utility helpers to read repo metadata from repos.yml without external deps."""
from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    try:
        digits = value
        if digits and digits[0] in "+-":
            digits_body = digits[1:]
        else:
            digits_body = digits
        if digits_body.startswith("0") and len(digits_body) > 1 and digits_body.isdigit():
            raise ValueError
        return int(value)
    except ValueError:
        pass
    float_markers = {"nan", "+nan", "-nan", "inf", "+inf", "-inf"}
    if any(ch in value for ch in ".eE") or lowered in float_markers:
        try:
            return float(value)
        except ValueError:
            pass
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def strip_comments(raw_line: str) -> str:
    result_chars: List[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(raw_line):
        ch = raw_line[i]
        if ch == "'" and not in_double:
            if in_single and i + 1 < len(raw_line) and raw_line[i + 1] == "'":
                result_chars.append("'")
                i += 2
                continue
            in_single = not in_single
            result_chars.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            backslashes = 0
            j = i - 1
            while j >= 0 and raw_line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                in_double = not in_double
            result_chars.append(ch)
            i += 1
            continue
        if ch == "#" and not in_single and not in_double:
            break
        result_chars.append(ch)
        i += 1
    return "".join(result_chars).rstrip()


def preprocess_lines(text: str) -> List[Tuple[int, str]]:
    lines: List[Tuple[int, str]] = []
    for raw_line in text.splitlines():
        without_comment = strip_comments(raw_line)
        if not without_comment.strip():
            continue
        indent = len(without_comment) - len(without_comment.lstrip(" "))
        lines.append((indent, without_comment.strip()))
    return lines


def parse_child_block(
    lines: List[Tuple[int, str]], start: int, parent_indent: int
) -> Tuple[Any, int]:
    """Parse a nested block at *start* or return ``None`` when no child block follows."""

    if start >= len(lines):
        return None, start
    child_indent = lines[start][0]
    if child_indent <= parent_indent:
        return None, start
    return parse_block(lines, start, child_indent)


def parse_block(lines: List[Tuple[int, str]], start: int, indent: int) -> Tuple[Any, int]:
    mapping: Dict[str, Any] = {}
    sequence: List[Any] | None = None
    i = start
    while i < len(lines):
        current_indent, content = lines[i]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"Unexpected indent {current_indent} (expected {indent})")
        if content.startswith("- "):
            if mapping:
                raise ValueError("Cannot mix mapping and sequence at same level")
            if sequence is None:
                sequence = []
            item_body = content[2:].strip()
            if not item_body:
                value, i = parse_child_block(lines, i + 1, indent)
                sequence.append(value)
                continue
            if item_body.endswith(":"):
                key = item_body[:-1].strip()
                value, i = parse_child_block(lines, i + 1, indent)
                sequence.append({key: value})
                continue
            colon_index = item_body.find(":")
            if colon_index != -1 and (
                colon_index == len(item_body) - 1
                or item_body[colon_index + 1] in " \t"
            ):
                key, raw_value = item_body.split(":", 1)
                item: Dict[str, Any] = {key.strip(): parse_scalar(raw_value)}
                has_child = False
                peek = i + 1
                while peek < len(lines):
                    peek_indent, _ = lines[peek]
                    if peek_indent <= indent:
                        break
                    has_child = True
                    break
                if has_child:
                    extra, i = parse_child_block(lines, i + 1, indent)
                    if not isinstance(extra, dict):
                        raise ValueError("Expected mapping for nested list item")
                    item.update(extra)
                    sequence.append(item)
                    continue
                sequence.append(item)
                i += 1
                continue
            sequence.append(parse_scalar(item_body))
            i += 1
            continue
        if content == "-":
            if mapping:
                raise ValueError("Cannot mix mapping and sequence at same level")
            if sequence is None:
                sequence = []
            value, i = parse_child_block(lines, i + 1, indent)
            sequence.append(value)
            continue
        if sequence is not None:
            raise ValueError("Cannot mix mapping and sequence at same level")
        if content.endswith(":"):
            key = content[:-1].strip()
            value, i = parse_child_block(lines, i + 1, indent)
            mapping[key] = value
            continue
        if ":" in content:
            key, raw_value = content.split(":", 1)
            mapping[key.strip()] = parse_scalar(raw_value)
            i += 1
            continue
        raise ValueError(f"Unsupported YAML construct: {content}")
    return (sequence if sequence is not None else mapping), i


def parse_simple_yaml(text: str) -> Any:
    lines = preprocess_lines(text)
    if not lines:
        return {}
    value, index = parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        result: Dict[str, Any] = {}
        if isinstance(value, dict):
            result.update(value)
        else:
            raise ValueError("Unexpected non-mapping at root of YAML document")
        while index < len(lines):
            block_value, index = parse_block(lines, index, lines[index][0])
            if not isinstance(block_value, dict):
                raise ValueError("Expected mapping entries at root level")
            result.update(block_value)
        return result
    return value


def to_repo_object(entry: Any) -> Dict[str, Any]:
    if isinstance(entry, str):
        return {"name": entry}
    if isinstance(entry, dict):
        return dict(entry)
    raise ValueError(f"Unsupported repo entry: {entry!r}")


def gather_repos(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    repos: List[Dict[str, Any]] = []
    seen: Dict[str, Dict[str, Any]] = {}
    lists: List[Iterable[Any]] = []
    if isinstance(data.get("repos"), list):
        lists.append(data["repos"])
    static_data = data.get("static")
    if isinstance(static_data, dict):
        include = static_data.get("include")
        if isinstance(include, list):
            lists.append(include)
    for lst in lists:
        for item in lst:
            repo = to_repo_object(item)
            name = repo.get("name")
            if not name:
                continue
            if name in seen:
                seen[name].update(repo)
            else:
                seen[name] = repo
    repos.extend(seen.values())
    return repos


def ordered_repo_names(repos: List[Dict[str, Any]]) -> List[str]:
    graph = {repo["name"]: set() for repo in repos}
    in_degree = {name: 0 for name in graph}
    for repo in repos:
        name = repo["name"]
        deps = repo.get("depends_on") or []
        if isinstance(deps, str):
            deps = [deps]
        for dep in deps:
            if dep not in graph:
                continue
            if name not in graph[dep]:
                graph[dep].add(name)
                in_degree[name] += 1
    heap: List[str] = [name for name, deg in in_degree.items() if deg == 0]
    heapq.heapify(heap)
    order: List[str] = []
    while heap:
        current = heapq.heappop(heap)
        order.append(current)
        for neighbor in sorted(graph[current]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    if len(order) < len(graph):
        remaining = sorted(set(graph) - set(order))
        order.extend(remaining)
    return order


def load_config(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = parse_simple_yaml(text)
    if not isinstance(data, dict):
        raise ValueError("Expected mapping at root of repos.yml")
    return data


def cmd_mode(data: Dict[str, Any]) -> None:
    mode = data.get("mode")
    if isinstance(mode, str) and mode.strip():
        print(mode.strip())
    else:
        print("static")


def cmd_owner(data: Dict[str, Any]) -> None:
    github = data.get("github")
    if isinstance(github, dict):
        owner = github.get("owner")
        if isinstance(owner, str) and owner.strip():
            print(owner.strip())
            return
    print("")


def cmd_repos(data: Dict[str, Any], ordered: bool, as_json: bool) -> None:
    repos = gather_repos(data)
    if ordered:
        names = ordered_repo_names(repos)
    else:
        names = sorted(repo["name"] for repo in repos)
    if as_json:
        print(json.dumps(names))
    else:
        for name in names:
            print(name)


def cmd_repo_rows(data: Dict[str, Any]) -> None:
    repos = gather_repos(data)
    for repo in repos:
        name = repo.get("name", "")
        default_branch = repo.get("default_branch", "main")
        url = repo.get("url", "")
        depends = repo.get("depends_on") or []
        if isinstance(depends, str):
            depends = [depends]
        depends_str = ",".join(depends)
        print(f"{name}\t{default_branch}\t{url}\t{depends_str}")


def cmd_repo_info(data: Dict[str, Any], name: str) -> None:
    repos = gather_repos(data)
    for repo in repos:
        if repo.get("name") == name:
            print(json.dumps(repo))
            return
    raise SystemExit(f"Repo not found: {name}")


def cmd_default_branch(data: Dict[str, Any], name: str) -> None:
    repos = gather_repos(data)
    for repo in repos:
        if repo.get("name") == name:
            default_branch = repo.get("default_branch", "main")
            print(default_branch)
            return
    print("main")


def cmd_validate(data: Dict[str, Any]) -> None:
    _ = gather_repos(data)
    print("OK")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read metadata from repos.yml")
    parser.add_argument("--file", default="repos.yml", help="Path to repos.yml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("mode")
    sub.add_parser("owner")

    repos_parser = sub.add_parser("repos")
    repos_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit repo names as JSON instead of one per line",
    )

    ordered_repos_parser = sub.add_parser("ordered-repos")
    ordered_repos_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit ordered repo names as JSON instead of one per line",
    )

    sub.add_parser("repo-rows")

    repo_info = sub.add_parser("repo-info")
    repo_info.add_argument("name")

    default_branch = sub.add_parser("default-branch")
    default_branch.add_argument("name")

    sub.add_parser("validate")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"repos.yml not found: {path}")
    data = load_config(path)

    if args.command == "mode":
        cmd_mode(data)
    elif args.command == "owner":
        cmd_owner(data)
    elif args.command == "repos":
        cmd_repos(data, ordered=False, as_json=args.json)
    elif args.command == "ordered-repos":
        cmd_repos(data, ordered=True, as_json=args.json)
    elif args.command == "repo-rows":
        cmd_repo_rows(data)
    elif args.command == "repo-info":
        cmd_repo_info(data, args.name)
    elif args.command == "default-branch":
        cmd_default_branch(data, args.name)
    elif args.command == "validate":
        cmd_validate(data)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
