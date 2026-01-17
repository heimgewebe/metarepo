import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

# Path to the script
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_integrity_sources.py"

def test_generate_integrity_sources_standard(tmp_path):
    # Setup mock file structure
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    # Mock fleet/repos.yml
    fleet_repos_content = {
        "repos": [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "metarepo"}
        ]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    # Mock repos.yml
    repos_content = {
        "github": {"owner": "testorg"},
        "repos": [
            {"name": "repo1", "url": "https://..."},
            {"name": "repo2"},
            {"name": "metarepo"}
        ]
    }
    with open(tmp_path / "repos.yml", "w") as f:
        yaml.dump(repos_content, f)

    # Run the script
    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output
    output_file = tmp_path / "reports/integrity/sources.v1.json"
    assert output_file.exists()

    with open(output_file, "r") as f:
        data = json.load(f)

    assert data["apiVersion"] == "integrity.sources.v1"
    assert "generated_at" in data
    assert len(data["sources"]) == 3

    # Check content
    sources_map = {s["repo"]: s for s in data["sources"]}

    assert "testorg/repo1" in sources_map
    assert sources_map["testorg/repo1"]["summary_url"] == "https://github.com/testorg/repo1/releases/download/integrity/summary.json"
    assert sources_map["testorg/repo1"]["enabled"] is True

    assert "testorg/metarepo" in sources_map

def test_generate_integrity_sources_no_repo_config(tmp_path):
    # Setup mock file structure (without repos.yml)
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": ["simple-repo"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    # Run the script
    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    # Default owner should be heimgewebe
    assert data["sources"][0]["repo"] == "heimgewebe/simple-repo"
    assert "heimgewebe/simple-repo/releases" in data["sources"][0]["summary_url"]

def test_generate_integrity_sources_fleet_false_list(tmp_path):
    # Test fleet: false in list format
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": [
            {"name": "repo1", "fleet": True},
            {"name": "repo2", "fleet": False},
            {"name": "repo3"}  # implicit true
        ]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    repos = [s["repo"] for s in data["sources"]]
    assert "heimgewebe/repo1" in repos
    assert "heimgewebe/repo2" not in repos
    assert "heimgewebe/repo3" in repos

def test_generate_integrity_sources_dict_format(tmp_path):
    # Test repos as dict format
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": {
            "repo1": {"fleet": True},
            "repo2": {"fleet": False},
            "repo3": {} # implicit true
        }
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    repos = [s["repo"] for s in data["sources"]]
    assert "heimgewebe/repo1" in repos
    assert "heimgewebe/repo2" not in repos
    assert "heimgewebe/repo3" in repos
