#!/usr/bin/env python3
"""Generate a read-only Fleet readiness report from canonical Fleet truth."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import must follow the repository-root path bootstrap above.
from wgx import repo_config  # noqa: E402

WgxProfileKind = Literal["profile", "no_profile", "missing"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_org_root() -> Path:
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def load_repo_configs(path: Path) -> Dict[str, Dict[str, Any]]:
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
    wgx_config = config.get("wgx", {})
    if isinstance(wgx_config, dict) and wgx_config.get("profile_expected") is False:
        return "no_profile"
    return "missing"


def has_ci(repo: Path) -> bool:
    workflows = repo / ".github" / "workflows"
    return workflows.exists() and any(path.suffix in {".yml", ".yaml"} for path in workflows.iterdir())


def has_contracts_marker(repo: Path) -> bool:
    return (repo / "contracts").exists() or (repo / ".contracts").exists() or (repo / "CONTRACTS.md").exists()


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--fleet-file", default="fleet/repos.yml")
    parser.add_argument("--repos-yml", default="repos.yml")
    parser.add_argument("--out-json", default="reports/heimgewebe-readiness.json")
    parser.add_argument(
        "--write-repos-txt",
        help="optional path for explicitly generating the fleet repos.txt projection",
    )
    args = parser.parse_args()

    metarepo_root = ROOT
    org_root = detect_org_root()
    fleet_data = repo_config.load_config(metarepo_root / args.fleet_file)
    fleet = repo_config.active_fleet_names(fleet_data)
    repo_configs = load_repo_configs(metarepo_root / args.repos_yml)

    if args.write_repos_txt:
        output = metarepo_root / args.write_repos_txt
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(fleet) + "\n", encoding="utf-8")

    repos: List[RepoReadiness] = []
    for name in fleet:
        repo_path = metarepo_root if name == "metarepo" else org_root / name
        if not repo_path.exists():
            repos.append(RepoReadiness(name, str(repo_path), True, False, "missing", False, False))
            continue
        kind = wgx_profile_kind(repo_path, repo_configs.get(name, {}))
        repos.append(RepoReadiness(
            name=name,
            path=str(repo_path),
            missing_repo=False,
            has_wgx_profile=kind != "missing",
            wgx_profile_kind=kind,
            has_ci=has_ci(repo_path),
            has_contracts_marker=has_contracts_marker(repo_path),
        ))

    report = {
        "generated_at": utc_now_iso(),
        "source": {
            "kind": "canonical_fleet_membership",
            "path": args.fleet_file,
            "does_not_establish": ["runtime health", "repository availability outside this observation"],
        },
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
        "repos": [asdict(repo) for repo in repos],
    }
    out_json = metarepo_root / args.out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("✅ readiness written:", out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
