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
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Dict, Literal

# Ensure the repository root is in the path for wgx imports
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from wgx import repo_config


WgxProfileKind = Literal["profile", "no_profile", "missing"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_org_root() -> Path:
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
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


def load_repo_configs(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load repos.yml and return a dict of name -> config."""
    if not path.exists():
        return {}
    data = repo_config.load_config(path)
    repos_list = repo_config.gather_repos(data)
    return {r["name"]: r for r in repos_list if "name" in r}


def wgx_profile_kind(repo: Path, config: Dict[str, Any]) -> WgxProfileKind:
    if (repo / ".wgx" / "profile.yml").exists():
        return "profile"
    if (repo / ".wgx" / "NO_PROFILE").exists():
        return "no_profile"

    # Check config for exception
    wgx_config = config.get("wgx", {})
    if wgx_config.get("profile_expected") is False:
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
    ap.add_argument("--repos-yml", default="repos.yml")
    ap.add_argument("--out-json", default="reports/heimgewebe-readiness.json")
    ap.add_argument("--write-repos-txt", default="fleet/repos.txt")
    args = ap.parse_args()

    metarepo_root = Path(__file__).resolve().parents[2]
    org_root = detect_org_root()

    fleet = parse_repo_matrix(metarepo_root / args.matrix)
    repo_configs = load_repo_configs(metarepo_root / args.repos_yml)

    # write derived repos.txt
    if args.write_repos_txt:
        out = metarepo_root / args.write_repos_txt
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(fleet) + "\n", encoding="utf-8")

    repos: List[RepoReadiness] = []
    for name in fleet:
        if name == "metarepo":
            rp = metarepo_root
        else:
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

        config = repo_configs.get(name, {})
        kind = wgx_profile_kind(rp, config)
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
