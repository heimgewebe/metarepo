#!/usr/bin/env python3
"""
Generates the fleet documentation (docs/_generated/fleet.md) from fleet/repos.yml.
Uses a simple internal YAML parser since PyYAML is not available in the base environment.
"""

import sys
import os
from datetime import datetime
import subprocess

# Add repo root to sys.path to import wgx.repo_config
sys.path.append(os.getcwd())

try:
    from wgx.repo_config import load_repo_config
except ImportError:
    # Fallback if wgx package is not found or structure differs
    # We will implement a very simple parser sufficient for fleet/repos.yml
    pass

FLEET_FILE = "fleet/repos.yml"
OUTPUT_FILE = "docs/_generated/fleet.md"

def simple_yaml_load(filepath):
    """
    Very basic YAML parser for fleet/repos.yml structure.
    Returns a dict with 'repos' (list of dicts) and 'static' (dict with 'include' list).
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    data = {"repos": [], "static": {"include": []}}
    current_section = None
    current_subsection = None

    for line in lines:
        line = line.rstrip()
        if not line or line.startswith("#") or line == "---":
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith("static:"):
            current_section = "static"
            continue
        elif stripped.startswith("repos:"):
            current_section = "repos"
            continue

        if current_section == "repos":
            if stripped.startswith("- name:"):
                name = stripped.replace("- name:", "").strip()
                data["repos"].append({"name": name})

        elif current_section == "static":
            if stripped.startswith("include:"):
                current_subsection = "include"
                continue

            if current_subsection == "include":
                if stripped.startswith("- name:"):
                    # Start of a new item
                    name = stripped.replace("- name:", "").strip()
                    # Look ahead/behind logic is hard in single pass line loop without state object
                    # Simplified: We just grab the name.
                    # If we need status/fleet props, we need a better parser.
                    # Given the environment constraints, let's try to parse block items.
                    data["static"]["include"].append({"name": name})
                elif stripped.startswith("status:") or stripped.startswith("fleet:") or stripped.startswith("url:"):
                     # Add property to last item
                     if data["static"]["include"]:
                         key, val = stripped.split(":", 1)
                         val = val.strip().strip('"')
                         if val.lower() == "true": val = True
                         if val.lower() == "false": val = False
                         data["static"]["include"][-1][key] = val

    return data

def get_git_info():
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return commit_hash, date
    except:
        return "unknown", datetime.now().strftime("%Y-%m-%d")

def generate_fleet_docs():
    if not os.path.exists(FLEET_FILE):
        print(f"Error: {FLEET_FILE} not found.")
        sys.exit(1)

    # Use simple parser
    data = simple_yaml_load(FLEET_FILE)

    commit_hash, date = get_git_info()

    content = []
    content.append("<!-- GENERATED FILE - DO NOT EDIT -->")
    content.append("<!-- Source: fleet/repos.yml -->")
    content.append(f"<!-- Generated at: {date} (Commit: {commit_hash}) -->")
    content.append("")
    content.append("# Heimgewebe Fleet Overview")
    content.append("")
    content.append("> **Note:** This document is automatically generated from [`fleet/repos.yml`](../../fleet/repos.yml).")
    content.append("")

    # Core Fleet
    content.append("## Core Fleet")
    content.append("Repositories managed by WGX (Contracts, Templates, Policies).")
    content.append("")

    if "repos" in data and data["repos"]:
        for repo in data["repos"]:
            name = repo.get("name")
            if name:
                content.append(f"- **{name}**")
    else:
        content.append("_No core repos defined._")

    content.append("")

    # Static / Related
    content.append("## Related / Static")
    content.append("Repositories that are part of the ecosystem but have specific roles.")
    content.append("")

    if "static" in data and "include" in data["static"]:
        for repo in data["static"]["include"]:
            name = repo.get("name")
            status = repo.get("status", "unknown")
            fleet = repo.get("fleet", True)
            fleet_marker = ""
            if fleet is False:
                fleet_marker = " (Non-Fleet)"
            elif fleet is True and status == "related":
                 pass

            content.append(f"- **{name}** ({status}){fleet_marker}")
    else:
        content.append("_No related repos defined._")

    content.append("")
    content.append("---")
    content.append(f"_Generated by scripts/fleet/generate_fleet_docs.py_")

    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(content))

    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_fleet_docs()
