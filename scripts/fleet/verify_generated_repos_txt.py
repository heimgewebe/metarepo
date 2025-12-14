#!/usr/bin/env python3
"""
Verify that fleet/repos.txt is exactly the generated output from docs/repo-matrix.md.

This is stronger than set-equality drift checks:
- order must match
- whitespace and trailing newline must match

If it fails, CI prints a fix hint.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path
from typing import List


def parse_repo_matrix_fleet_yes(matrix_path: Path) -> List[str]:
    import re

    if not matrix_path.exists():
        raise FileNotFoundError(f"Missing file: {matrix_path}")

    lines = matrix_path.read_text(encoding="utf-8").splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^\|\s*Repo\s*\|\s*Rolle\s*\|\s*Fleet\s*\|\s*$", line.strip()):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"Could not find repo-matrix header row in {matrix_path}")

    repos_yes: List[str] = []
    for line in lines[header_idx + 2 :]:
        s = line.strip()
        if not s.startswith("|"):
            break
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 3:
            continue
        repo, _rolle, fleet = cols[0], cols[1], cols[2]
        if fleet.lower() == "yes":
            repos_yes.append(repo)

    if not repos_yes:
        raise ValueError(f"No 'Fleet yes' repos parsed from {matrix_path}")
    return repos_yes


def expected_repos_txt_content(repos: List[str]) -> str:
    # Deterministic: one repo per line + trailing newline.
    return "\n".join(repos) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default="docs/repo-matrix.md")
    ap.add_argument("--fleet", default="fleet/repos.txt")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]  # metarepo root
    matrix_path = (repo_root / args.matrix).resolve()
    fleet_path = (repo_root / args.fleet).resolve()

    repos = parse_repo_matrix_fleet_yes(matrix_path)
    expected = expected_repos_txt_content(repos)

    if not fleet_path.exists():
        print(f"❌ Missing derived file: {fleet_path}")
        print("Fix: run the generator or create fleet/repos.txt from docs/repo-matrix.md.")
        return 1

    actual = fleet_path.read_text(encoding="utf-8")

    if actual == expected:
        print("✅ fleet/repos.txt matches generated output exactly.")
        return 0

    print("❌ fleet/repos.txt does not match generated output.")
    print("Diff (expected -> actual):")
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected (generated)",
        tofile="actual (committed)",
    )
    sys.stdout.writelines(diff)
    print()
    print("Fix:")
    print("  - Update docs/repo-matrix.md OR")
    print("  - Regenerate fleet/repos.txt using scripts/fleet/generate_readiness.py with --write-repos-txt fleet/repos.txt")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
