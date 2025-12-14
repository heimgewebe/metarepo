#!/usr/bin/env python3
"""
hg-doctor: Fleet readiness diagnostics

Reads:
  - reports/heimgewebe-readiness.json (preferred)

Or generates it if missing (optional flag).

Outputs:
  - human-readable summary
  - exit codes for CI

Exit codes:
  0 = OK (no critical findings)
  2 = WARN (warnings only)
  3 = CRITICAL (critical findings)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


CRITICAL_CODE = 3
WARN_CODE = 2
OK_CODE = 0


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_generate_readiness(matrix: str, out_json: str, write_repos_txt: str) -> int:
    cmd = [
        sys.executable,
        "scripts/fleet/generate_readiness.py",
        "--matrix",
        matrix,
        "--out-json",
        out_json,
        "--write-repos-txt",
        write_repos_txt,
    ]
    return subprocess.call(cmd, cwd=str(repo_root()))


def classify(findings: Dict[str, List[str]], is_ci: bool) -> int:
    # Critical if missing wgx profile in any existing repo.
    if findings["missing_wgx_profile"]:
        return CRITICAL_CODE

    # Missing repos are CRITICAL locally, but accepted (ignored) in CI.
    if findings["missing_repo"] and not is_ci:
        return CRITICAL_CODE

    # Warnings (e.g. missing CI workflows in existing repos)
    if findings["missing_ci"] or findings["missing_contracts_marker"]:
        return WARN_CODE

    return OK_CODE


def summarize(repos: List[Dict]) -> Dict[str, List[str]]:
    missing_repo: List[str] = []
    missing_wgx_profile: List[str] = []
    missing_ci: List[str] = []
    missing_contracts_marker: List[str] = []

    for r in repos:
        name = r.get("name", "?")
        if r.get("missing_repo"):
            missing_repo.append(name)
            continue
        if not r.get("has_wgx_profile", False):
            missing_wgx_profile.append(name)
        if not r.get("has_ci", False):
            missing_ci.append(name)
        if not r.get("has_contracts_marker", False):
            missing_contracts_marker.append(name)

    return {
        "missing_repo": sorted(missing_repo),
        "missing_wgx_profile": sorted(missing_wgx_profile),
        "missing_ci": sorted(missing_ci),
        "missing_contracts_marker": sorted(missing_contracts_marker),
    }


def print_block(title: str, items: List[str]) -> None:
    if not items:
        return
    print()
    print(title)
    for it in items:
        print(f"  - {it}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="reports/heimgewebe-readiness.json", help="Readiness report path.")
    ap.add_argument("--generate-if-missing", action="store_true", help="Generate report if missing.")
    ap.add_argument("--matrix", default="docs/repo-matrix.md", help="Repo matrix for generation.")
    ap.add_argument("--write-repos-txt", default="fleet/repos.txt", help="Write derived repos list during generation.")
    ap.add_argument("--ci", action="store_true", help="CI mode: nonzero exit on WARN/CRITICAL.")
    args = ap.parse_args()

    root = repo_root()
    report_path = (root / args.report).resolve()

    if not report_path.exists():
        if not args.generate_if_missing:
            print(f"❌ Missing readiness report: {report_path}")
            print("Fix: run `just fleet` / `make fleet` or re-run with --generate-if-missing.")
            return CRITICAL_CODE
        rc = run_generate_readiness(args.matrix, args.report, args.write_repos_txt)
        if rc != 0:
            print("❌ Failed to generate readiness report.")
            return CRITICAL_CODE

    data = load_json(report_path)
    generated_at = data.get("generated_at", "?")
    org_root = data.get("org_root", "?")
    defaults = data.get("defaults", {})
    repos = data.get("repos", [])

    findings = summarize(repos)
    level = classify(findings, is_ci=args.ci)

    print("hg-doctor — Heimgewebe Fleet Diagnostics")
    print("--------------------------------------")
    print(f"generated_at: {generated_at}")
    print(f"org_root:     {org_root}")
    print(f"defaults:     profile={defaults.get('profile')} render={defaults.get('render')} split_part_mb={defaults.get('split_part_mb')} max_file_bytes={defaults.get('max_file_bytes')}")
    feats = defaults.get("features", {})
    if feats:
        enabled = [k for k, v in feats.items() if v]
        print(f"features:     {', '.join(sorted(enabled))}")

    if level == OK_CODE:
        print()
        print("✅ STATUS: OK — Fleet coherence looks good.")
    elif level == WARN_CODE:
        print()
        print("⚠️ STATUS: WARN — Some repos are missing recommended markers.")
    else:
        print()
        print("❌ STATUS: CRITICAL — Fleet coherence is broken.")

    print_block("Missing repos (not found under org_root):", findings["missing_repo"])
    print_block("Repos missing .wgx/profile.yml:", findings["missing_wgx_profile"])
    print_block("Repos missing CI workflows (.github/workflows/*.yml):", findings["missing_ci"])
    print_block("Repos missing contracts marker:", findings["missing_contracts_marker"])

    # Exit behavior
    if args.ci:
        return level
    # In interactive mode, always return 0 so it doesn't annoy shells.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
