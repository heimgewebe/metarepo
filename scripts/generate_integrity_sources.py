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
from typing import Any

# Ensure the repository root is in the path for wgx imports
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

def load_yaml(yaml_mod: Any, path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml_mod.safe_load(f)

def utc_now_iso() -> str:
    # Support SOURCE_DATE_EPOCH for reproducible builds
    if "SOURCE_DATE_EPOCH" in os.environ:
        ts = int(os.environ["SOURCE_DATE_EPOCH"])
        return datetime.fromtimestamp(ts, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def detect_repo_root() -> Path:
    env = os.environ.get("HG_ROOT") or os.environ.get("HEIMGEWEBE_ROOT")
    if env:
        return Path(env).resolve()
    return _REPO_ROOT

def main():
    try:
        import yaml
    except ModuleNotFoundError:
        # Metarepo Control Plane requires PyYAML via uv
        sys.exit("Error: pyyaml not installed. Please run via 'uv run scripts/generate_integrity_sources.py'.")

    repo_root = detect_repo_root()
    fleet_repos_file = repo_root / "fleet/repos.yml"
    repos_yml_file = repo_root / "repos.yml"
    output_file = repo_root / "reports/integrity/sources.v1.json"

    # Load Fleet Membership
    if not fleet_repos_file.exists():
        print(f"Error: {fleet_repos_file} not found.")
        sys.exit(1)

    fleet_data = load_yaml(yaml, fleet_repos_file)

    fleet_list = []

    # Robust parsing of fleet/repos.yml
    if "repos" in fleet_data:
        repos_node = fleet_data["repos"]

        if isinstance(repos_node, list):
            for entry in repos_node:
                if isinstance(entry, dict):
                    name = entry.get("name")
                    if not name:
                        continue
                    # Check for explicit fleet: false in list items
                    if entry.get("fleet") is False:
                        continue
                    fleet_list.append(name)
                elif isinstance(entry, str):
                    fleet_list.append(entry)

        elif isinstance(repos_node, dict):
            # Dict form: { "repo_name": { ... metadata ... } }
            for name, meta in repos_node.items():
                if isinstance(meta, dict):
                    # Filter out if fleet is explicitly false
                    if meta.get("fleet") is False:
                        continue
                    fleet_list.append(name)
                else:
                    # Treat simple key as valid repo
                    fleet_list.append(name)

    # Load Repo Configs (for overrides/owner)
    repo_configs = {}
    default_owner = "heimgewebe"

    if repos_yml_file.exists():
        raw_repos = load_yaml(yaml, repos_yml_file)
        default_owner = raw_repos.get("github", {}).get("owner", default_owner)

        if "repos" in raw_repos and isinstance(raw_repos["repos"], list):
            for r in raw_repos["repos"]:
                name = r.get("name")
                if name:
                    repo_configs[name] = r

    if not fleet_list:
        print(
            f"Warning: No repositories found in {fleet_repos_file}; generated sources list will be empty.",
            file=sys.stderr,
        )

    sources = []
    seen_repos = set()

    for repo_name in sorted(fleet_list):
        config = repo_configs.get(repo_name, {})
        # config usage: specifically to check for integrity.enabled override

        # Use default owner for all repos (per-repo owner override not currently supported)
        owner = default_owner
        full_repo_name = f"{owner}/{repo_name}"

        if full_repo_name in seen_repos:
            print(f"Error: Duplicate repo detected: {full_repo_name}", file=sys.stderr)
            sys.exit(1)
        seen_repos.add(full_repo_name)

        # Determine URL
        # Contract: https://github.com/<owner>/<repo>/releases/download/integrity/summary.json
        summary_url = f"https://github.com/{owner}/{repo_name}/releases/download/integrity/summary.json"

        # Check if enabled via overrides
        # Logic: fleet implies enabled, unless explicitly disabled in repos.yml metadata
        enabled = True
        integrity_config = config.get("integrity", {})
        if isinstance(integrity_config, dict) and integrity_config.get("enabled") is False:
            enabled = False

        sources.append({
            "repo": full_repo_name,
            "summary_url": summary_url,
            "enabled": enabled
        })

    # Check for idempotence to avoid drift in timestamps
    existing_data = None
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    new_generated_at = utc_now_iso()

    if existing_data and existing_data.get("sources") == sources:
        # Content didn't change, preserve timestamp to avoid noise
        new_generated_at = existing_data.get("generated_at", new_generated_at)
        print(f"No changes detected for {output_file}, preserving timestamp.")
    else:
        print(f"Changes detected, updating {output_file}")

    output_data = {
        "apiVersion": "integrity.sources.v1",
        "generated_at": new_generated_at,
        "sources": sources
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        f.write("\n")

if __name__ == "__main__":
    main()
