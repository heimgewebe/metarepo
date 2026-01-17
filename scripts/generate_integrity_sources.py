#!/usr/bin/env python3
"""
Generate the canonical list of integrity sources (Pull-Model).

Source of truth:
  - fleet/repos.yml (Fleet membership)
  - repos.yml (Metadata, overrides)

Output:
  - reports/integrity/sources.v1.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure the repository root is in the path for wgx imports
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Try to import repo_config, but handle failure gracefully
try:
    from wgx import repo_config
    HAS_WGX = True
except ImportError:
    HAS_WGX = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def load_yaml(path: Path) -> Any:
    if HAS_YAML:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    if HAS_WGX:
        return repo_config.load_config(path)
    # Fallback manual parsing or error
    raise ImportError("No yaml parser available (install pyyaml or wgx module)")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def detect_repo_root() -> Path:
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
    if env:
        return Path(env).resolve()
    return _REPO_ROOT

def main():
    repo_root = detect_repo_root()
    fleet_repos_file = repo_root / "fleet/repos.yml"
    repos_yml_file = repo_root / "repos.yml"
    output_file = repo_root / "reports/integrity/sources.v1.json"

    # Load Fleet Membership
    if not fleet_repos_file.exists():
        print(f"Error: {fleet_repos_file} not found.")
        sys.exit(1)

    fleet_data = load_yaml(fleet_repos_file)

    fleet_list = []
    if "repos" in fleet_data and isinstance(fleet_data["repos"], list):
        for entry in fleet_data["repos"]:
            if isinstance(entry, dict) and "name" in entry:
                fleet_list.append(entry["name"])
            elif isinstance(entry, str):
                fleet_list.append(entry)

    # Load Repo Configs (for overrides/owner)
    repo_configs = {}
    default_owner = "heimgewebe"

    if repos_yml_file.exists():
        raw_repos = load_yaml(repos_yml_file)
        default_owner = raw_repos.get("github", {}).get("owner", default_owner)

        if "repos" in raw_repos and isinstance(raw_repos["repos"], list):
            for r in raw_repos["repos"]:
                name = r.get("name")
                if name:
                    repo_configs[name] = r

    sources = []
    for repo_name in sorted(fleet_list):
        config = repo_configs.get(repo_name, {})
        # repos.yml entry doesn't strictly have 'owner', but root has github.owner
        # We assume all are under default owner unless specified (not currently supported in repos.yml schema but good for logic)
        owner = default_owner

        # Determine URL
        # Contract: https://github.com/<owner>/<repo>/releases/download/integrity/summary.json
        summary_url = f"https://github.com/{owner}/{repo_name}/releases/download/integrity/summary.json"

        # Check if enabled? Assume all fleet repos are enabled.
        enabled = True

        sources.append({
            "repo": f"{owner}/{repo_name}",
            "summary_url": summary_url,
            "enabled": enabled
        })

    output_data = {
        "apiVersion": "integrity.sources.v1",
        "generated_at": utc_now_iso(),
        "sources": sources
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        f.write("\n")

    print(f"Generated {output_file}")

if __name__ == "__main__":
    main()
