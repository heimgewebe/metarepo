#!/usr/bin/env python3
"""
Generate a machine-readable readiness report for the Heimgewebe fleet.

Source of truth:
  - docs/repo-matrix.md (Fleet=yes)

Optional derived outputs:
  - fleet/repos.txt (cache/derivative list)
  - reports/heimgewebe-readiness.json (report)

This script is intentionally conservative:
  - It never modifies other repos.
  - It never fails hard just because a repo path is missing; it records it.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_repo_root() -> Path:
    """
    Determine a default org root.
    Typical layout:
      <org_root>/
        metarepo/   (this repo)
        chronik/
        semantAH/
        ...
    If HG_ROOT is set, it wins.
    Otherwise, assume this script is running inside metarepo and pick its parent.
    """
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEBEWE_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # metarepo root is two parents up from scripts/fleet/
    # scripts/fleet/generate_readiness.py -> scripts/fleet -> scripts -> repo_root
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root.parent.resolve()


# --- parsing: reuse logic by importing the drift-check parser (single place of truth) ---
def parse_repo_matrix_fleet_yes(matrix_path: Path) -> List[str]:
    """
    Parse docs/repo-matrix.md and return repos where Fleet == 'yes',
    preserving the order in the matrix.

    We intentionally keep this function local (instead of importing)
    to avoid circular dependencies if tools evolve.
    """
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


def has_any_workflow(repo_path: Path) -> bool:
    wf_dir = repo_path / ".github" / "workflows"
    if not wf_dir.exists() or not wf_dir.is_dir():
        return False
    return any(p.suffix in (".yml", ".yaml") for p in wf_dir.iterdir() if p.is_file())


def has_contracts_marker(repo_path: Path) -> bool:
    """
    Marker heuristic:
      - contracts/ folder
      - .contracts/ folder
      - CONTRACTS.md
      - contracts-index.md (common meta file)
    """
    if (repo_path / "contracts").exists():
        return True
    if (repo_path / ".contracts").exists():
        return True
    if (repo_path / "CONTRACTS.md").exists():
        return True
    if (repo_path / "contracts-index.md").exists():
        return True
    return False


def has_wgx_profile(repo_path: Path) -> bool:
    return (repo_path / ".wgx" / "profile.yml").exists()


@dataclass
class RepoReadiness:
    name: str
    path: str
    missing_repo: bool
    has_wgx_profile: bool
    has_ci: bool
    has_contracts_marker: bool


def build_defaults_block() -> Dict:
    # The same defaults you decided: dev, combined, split 25MB, no truncation, extras on.
    return {
        "profile": "dev",
        "render": "combined",
        "split_part_mb": 25,
        "max_file_bytes": 0,
        "features": {
            "health": True,
            "augment_sidecar": True,
            "organism_index": True,
            "fleet_panorama": True,
            "json_sidecar": True,
            "ai_heatmap": True,
        },
    }


def write_repos_txt(out_path: Path, repos: List[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(repos) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default="docs/repo-matrix.md", help="Repo matrix (source of truth).")
    ap.add_argument("--org-root", default="", help="Org root containing all repos. Env HG_ROOT also supported.")
    ap.add_argument("--out-json", default="reports/heimgewebe-readiness.json", help="Output report path.")
    ap.add_argument(
        "--write-repos-txt",
        default="fleet/repos.txt",
        help="Write derived repo list here (set empty to disable).",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]  # metarepo root
    matrix_path = (repo_root / args.matrix).resolve()

    if args.org_root:
        org_root = Path(args.org_root).expanduser().resolve()
    else:
        org_root = detect_repo_root()

    fleet = parse_repo_matrix_fleet_yes(matrix_path)

    # Optionally write derived fleet list
    if args.write_repos_txt:
        write_repos_txt((repo_root / args.write_repos_txt).resolve(), fleet)

    repos_out: List[RepoReadiness] = []
    for name in fleet:
        rp = (org_root / name).resolve()
        missing_repo = not rp.exists()
        if missing_repo:
            repos_out.append(
                RepoReadiness(
                    name=name,
                    path=str(rp),
                    missing_repo=True,
                    has_wgx_profile=False,
                    has_ci=False,
                    has_contracts_marker=False,
                )
            )
            continue

        repos_out.append(
            RepoReadiness(
                name=name,
                path=str(rp),
                missing_repo=False,
                has_wgx_profile=has_wgx_profile(rp),
                has_ci=has_any_workflow(rp),
                has_contracts_marker=has_contracts_marker(rp),
            )
        )

    out = {
        "generated_at": utc_now_iso(),
        "org_root": str(org_root),
        "defaults": build_defaults_block(),
        "repos": [asdict(r) for r in repos_out],
    }

    out_path = (repo_root / args.out_json).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Summarize to stdout (useful in CI logs)
    missing = [r.name for r in repos_out if r.missing_repo]
    no_wgx = [r.name for r in repos_out if not r.missing_repo and not r.has_wgx_profile]
    no_ci = [r.name for r in repos_out if not r.missing_repo and not r.has_ci]
    no_contracts = [r.name for r in repos_out if not r.missing_repo and not r.has_contracts_marker]

    print("✅ readiness report written:", out_path)
    if missing:
        print("⚠️ missing repos under org_root:", ", ".join(sorted(missing)))
    if no_wgx:
        print("ℹ️ repos missing .wgx/profile.yml:", ", ".join(sorted(no_wgx)))
    if no_ci:
        print("ℹ️ repos missing CI workflows:", ", ".join(sorted(no_ci)))
    if no_contracts:
        print("ℹ️ repos missing contracts marker:", ", ".join(sorted(no_contracts)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
