#!/usr/bin/env python3
"""
Drift-Check: fleet/repos.txt muss exakt der Core-Fleet aus docs/repo-matrix.md entsprechen.

Warum:
- docs/repo-matrix.md ist die menschenlesbare kanonische Definition (Fleet yes/no).
- fleet/repos.txt ist ein maschinenfreundliches Derivat für Scripts/CI.

Dieses Script failt, wenn die Listen auseinanderlaufen.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple


def read_repos_txt(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    repos: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        repos.append(line)
    return repos


def parse_repo_matrix_md(path: Path) -> List[str]:
    """
    Parse docs/repo-matrix.md markdown table:
    | Repo | Rolle | Fleet |
    Keep rows where Fleet == 'yes'.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()

    # Find header row index for the table, then parse subsequent pipe-rows.
    header_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^\|\s*Repo\s*\|\s*Rolle\s*\|\s*Fleet\s*\|\s*$", line.strip()):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"Could not find repo-matrix header row in {path}")

    repos_yes: List[str] = []
    for line in lines[header_idx + 2 :]:  # skip header + separator
        s = line.strip()
        if not s.startswith("|"):
            # stop when table ends
            break
        # Split into columns, ignore first/last empty due to leading/trailing '|'
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 3:
            continue
        repo, _rolle, fleet = cols[0], cols[1], cols[2]
        if fleet.lower() == "yes":
            repos_yes.append(repo)

    if not repos_yes:
        raise ValueError(f"No 'Fleet yes' repos parsed from {path}")
    return repos_yes


def diff_sets(a: Set[str], b: Set[str]) -> Tuple[Set[str], Set[str]]:
    return (a - b, b - a)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix",
        default="docs/repo-matrix.md",
        help="Path to docs/repo-matrix.md (source of truth).",
    )
    ap.add_argument(
        "--fleet",
        default="fleet/repos.txt",
        help="Path to fleet/repos.txt (derived list).",
    )
    args = ap.parse_args()

    matrix_path = Path(args.matrix)
    fleet_path = Path(args.fleet)

    truth = parse_repo_matrix_md(matrix_path)
    fleet = read_repos_txt(fleet_path)

    truth_set = set(truth)
    fleet_set = set(fleet)

    missing_in_fleet, extra_in_fleet = diff_sets(truth_set, fleet_set)

    # Also catch duplicates / ordering issues as warnings (not fail),
    # but fail hard on set mismatch.
    dupes = [r for r in fleet if fleet.count(r) > 1]
    dupes = sorted(set(dupes))

    if missing_in_fleet or extra_in_fleet:
        print("❌ Fleet drift detected:")
        if missing_in_fleet:
            print("  Missing in fleet/repos.txt (should be present):")
            for r in sorted(missing_in_fleet):
                print(f"    - {r}")
        if extra_in_fleet:
            print("  Extra in fleet/repos.txt (not in docs/repo-matrix.md Fleet=yes):")
            for r in sorted(extra_in_fleet):
                print(f"    - {r}")
        print()
        print("Fix: update fleet/repos.txt to match docs/repo-matrix.md (Fleet=yes).")
        return 1

    if dupes:
        print("⚠️ Warning: duplicates found in fleet/repos.txt:")
        for r in dupes:
            print(f"  - {r}")

    # Optional: enforce stable ordering matching the matrix list
    # (not failing for now; just suggest).
    if fleet != truth:
        print("ℹ️ Note: fleet/repos.txt order differs from docs/repo-matrix.md order.")
        print("Suggested order (from docs/repo-matrix.md):")
        for r in truth:
            print(r)

    print("✅ Fleet list matches docs/repo-matrix.md (Fleet=yes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
