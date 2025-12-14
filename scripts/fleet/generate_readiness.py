#!/usr/bin/env python3
"""
Generate a machine-readable readiness report for the Heimgewebe fleet.

Source of truth:
  - docs/repo-matrix.md   (Fleet=yes rows)

Derived artifacts:
  - fleet/repos.txt      (generated, never edited manually)
  - reports/heimgewebe-readiness.json

Design principles:
  - One truth, many exports
  - No crashes on missing repos
  - Explicit exceptions (NO_PROFILE) instead of fake profiles
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Literal


WgxProfileKind = Literal["profile", "no_profile", "missing"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_org_root() -> Path:
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEBEWE_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # assume: <org_root>/metarepo/scripts/fleet/generate_readiness.py
    return Path(__file__).resolve().parents[3]


def parse_repo_matrix(path: Path) -> List[str]:
    """
    Minimal parser:
    - expects a markdown table
    - includes rows where column 'Fleet' == 'yes'
    """
    repos: List[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    headers = []
    for line in lines:
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not headers:
            headers = cells
            continue
        if len(cells) != len(headers):
            continue
        row = dict(zip(headers, cells))
        if row.get("Fleet", "").lower() == "yes":
            repos.append(row["Repo"])
    return repos


def wgx_profile_kind(repo: Path) -> WgxProfileKind:
    if (repo / ".wgx" / "profile.yml").exists():
        return "profile"
    if (repo / ".wgx" / "NO_PROFILE").exists():
        return "no_profile"
    return "missing"


def has_ci(repo: Path) -> bool:
    wf = repo / ".github" / "workflows"
    return wf.exists() and any(p.suffix == ".yml" for p in wf.iterdir())


def has_contracts_marker(repo: Path) -> bool:
    return (
        (repo / "contracts").exists()
        or (repo / ".contracts").exists()
        or (repo / "CONTRACTS.md").exists()
    )


@dataclass
class RepoReadiness:
    name: str
    path: str
    missing_repo: bool
    has_wgx_profile: bool
    wgx_profile_kind: str
    has_ci: bool
    has_contracts_marker: bool


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default="docs/repo-matrix.md")
    ap.add_argument("--out-json", default="reports/heimgewebe-readiness.json")
    ap.add_argument("--write-repos-txt", default="fleet/repos.txt")
    args = ap.parse_args()

    metarepo_root = Path(__file__).resolve().parents[2]
    org_root = detect_org_root()

    fleet = parse_repo_matrix(metarepo_root / args.matrix)

    # write derived repos.txt
    if args.write_repos_txt:
        out = metarepo_root / args.write_repos_txt
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(fleet) + "\n", encoding="utf-8")

    repos: List[RepoReadiness] = []
    for name in fleet:
        rp = org_root / name
        if not rp.exists():
            repos.append(
                RepoReadiness(
                    name=name,
                    path=str(rp),
                    missing_repo=True,
                    has_wgx_profile=False,
                    wgx_profile_kind="missing",
                    has_ci=False,
                    has_contracts_marker=False,
                )
            )
            continue

        kind = wgx_profile_kind(rp)
        repos.append(
            RepoReadiness(
                name=name,
                path=str(rp),
                missing_repo=False,
                has_wgx_profile=(kind != "missing"),
                wgx_profile_kind=kind,
                has_ci=has_ci(rp),
                has_contracts_marker=has_contracts_marker(rp),
            )
        )

    report = {
        "generated_at": utc_now_iso(),
        "defaults": {
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
        },
        "repos": [asdict(r) for r in repos],
    }

    out_json = metarepo_root / args.out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("✅ readiness written:", out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
