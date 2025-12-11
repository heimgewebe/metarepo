#!/usr/bin/env python3
"""Clone fleet repositories defined in repos.yml into a local folder."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from wgx import repo_config


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _repo_url(repo: Mapping[str, object], owner: str | None) -> str:
    url = repo.get("url")
    if isinstance(url, str) and url.strip():
        return url.strip()
    name = repo.get("name")
    if isinstance(name, str) and name.strip() and owner:
        return f"https://github.com/{owner}/{name.strip()}.git"
    raise SystemExit(f"Missing url for repo entry: {repo}")


def _default_branch(repo: Mapping[str, object]) -> str:
    branch = repo.get("default_branch")
    if isinstance(branch, str) and branch.strip():
        return branch.strip()
    return "main"


def _clone_repo(url: str, target: Path, branch: str) -> bool:
    print(f"Cloning {url} -> {target} [branch: {branch}]")
    result = subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            branch,
            url,
            str(target),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout.strip())
        print(result.stderr.strip(), file=sys.stderr)
        return False
    return True


def _update_repo(target: Path, branch: str) -> bool:
    print(f"Updating {target} [branch: {branch}]")
    fetch = subprocess.run(
        ["git", "-C", str(target), "fetch", "--all", "--prune"],
        capture_output=True,
        text=True,
    )
    if fetch.returncode != 0:
        print(fetch.stdout.strip())
        print(fetch.stderr.strip(), file=sys.stderr)
        return False
    pull = subprocess.run(
        ["git", "-C", str(target), "pull", "--ff-only", "origin", branch],
        capture_output=True,
        text=True,
    )
    if pull.returncode != 0:
        print(pull.stdout.strip())
        print(pull.stderr.strip(), file=sys.stderr)
        return False
    return True


def _filter_repos(repos: Iterable[Dict[str, object]], names: List[str] | None) -> List[Dict[str, object]]:
    if not names:
        return list(repos)
    selected = {name.strip() for name in names if name.strip()}
    return [repo for repo in repos if repo.get("name") in selected]


def load_repos(manifest: Path) -> List[Dict[str, object]]:
    data = repo_config.load_config(manifest)
    repos = repo_config.gather_repos(data)
    repos.sort(key=lambda entry: str(entry.get("name", "")))
    return repos


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone heimgewebe fleet repositories defined in repos.yml",
    )
    parser.add_argument(
        "--repos-file",
        default="repos.yml",
        help="Path to the repos.yml manifest (default: repos.yml)",
    )
    parser.add_argument(
        "--dest",
        default="repos",
        help="Directory to clone repositories into (default: ./repos)",
    )
    parser.add_argument(
        "--owner",
        help="Override GitHub owner (falls back to repos.yml -> github.owner)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="If a repo already exists, fetch and fast-forward the default branch",
    )
    parser.add_argument(
        "names",
        nargs="*",
        help="Optional subset of repository names to clone",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = Path(args.repos_file)
    if not manifest.exists():
        raise SystemExit(f"repos file not found: {manifest}")

    repos = load_repos(manifest)
    owner = args.owner
    if not owner:
        data = repo_config.load_config(manifest)
        github = data.get("github") if isinstance(data, dict) else None
        if isinstance(github, dict):
            owner = github.get("owner") if isinstance(github.get("owner"), str) else None

    target_root = Path(args.dest)
    _ensure_directory(target_root)

    selection = _filter_repos(repos, args.names)
    if not selection:
        raise SystemExit("No repositories found for cloning")

    had_error = False
    for repo in selection:
        name = repo.get("name")
        if not isinstance(name, str) or not name.strip():
            print(f"Skipping invalid repo entry: {repo}")
            continue
        repo_name = name.strip()
        branch = _default_branch(repo)
        url = _repo_url(repo, owner)
        destination = target_root / repo_name

        if destination.exists():
            if args.update:
                ok = _update_repo(destination, branch)
                had_error = had_error or not ok
                continue
            print(f"Skipping {repo_name}: {destination} exists (use --update to pull)")
            continue

        ok = _clone_repo(url, destination, branch)
        had_error = had_error or not ok

    if had_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
