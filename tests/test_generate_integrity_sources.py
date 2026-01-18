import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml
from jsonschema import validate

# Path to the script
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_integrity_sources.py"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "contracts" / "integrity.sources.v1.schema.json"

def run_script(env):
    # Try to use uv if available, otherwise fallback to sys.executable
    cmd = [sys.executable, str(SCRIPT_PATH)]
    if shutil.which("uv"):
        cmd = ["uv", "run", str(SCRIPT_PATH)]

    return subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True
    )

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

    result = run_script(env)

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

    result = run_script(env)

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

    result = run_script(env)

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

    result = run_script(env)

    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    repos = [s["repo"] for s in data["sources"]]
    assert "heimgewebe/repo1" in repos
    assert "heimgewebe/repo2" not in repos
    assert "heimgewebe/repo3" in repos

def test_generate_integrity_sources_duplicate(tmp_path):
    # Test duplicate repo detection
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    # Same repo twice
    fleet_repos_content = {
        "repos": ["repo1", "repo1"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = run_script(env)

    assert result.returncode == 1
    assert "Duplicate repo detected" in result.stderr

def test_generate_integrity_sources_override_enabled(tmp_path):
    # Test integrity.enabled override
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": ["repo1"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    # Override enabled=False in repos.yml
    repos_content = {
        "repos": [
            {
                "name": "repo1",
                "integrity": {"enabled": False}
            }
        ]
    }
    with open(tmp_path / "repos.yml", "w") as f:
        yaml.dump(repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = run_script(env)

    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    assert data["sources"][0]["enabled"] is False

def test_generate_integrity_sources_idempotence(tmp_path):
    # Test that timestamp is preserved if content is unchanged
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": ["repo1"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    # First run
    run_script(env)
    output_file = tmp_path / "reports/integrity/sources.v1.json"

    with open(output_file, "r") as f:
        data1 = json.load(f)
    ts1 = data1["generated_at"]

    # Wait a moment to ensure clock advances
    time.sleep(1.1)

    # Second run (no config changes)
    run_script(env)

    with open(output_file, "r") as f:
        data2 = json.load(f)
    ts2 = data2["generated_at"]

    assert ts1 == ts2, "Timestamp should be preserved for identical content"

    # Third run (with change)
    fleet_repos_content["repos"].append("repo2")
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    run_script(env)

    with open(output_file, "r") as f:
        data3 = json.load(f)
    ts3 = data3["generated_at"]

    assert ts1 != ts3, "Timestamp should update when content changes"

def test_generated_output_matches_schema(tmp_path):
    # Test that generated output is valid against the schema
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": ["repo1"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = run_script(env)
    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)

    validate(instance=data, schema=schema)

def test_generate_integrity_sources_missing_fleet_file(tmp_path):
    # Test execution when fleet/repos.yml is missing
    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    # Do NOT create fleet/repos.yml

    result = run_script(env)

    assert result.returncode == 1
    assert "not found" in result.stdout

def test_generate_integrity_sources_empty_fleet(tmp_path):
    # Test warning on empty fleet list
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump({"repos": []}, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = run_script(env)

    assert result.returncode == 0
    assert "Warning: No fleet repositories found" in result.stderr

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    assert data["sources"] == []

def test_generate_integrity_sources_sorting(tmp_path):
    # Verify sources are sorted by repo name
    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()

    fleet_repos_content = {
        "repos": ["beta-repo", "alpha-repo"]
    }
    with open(fleet_dir / "repos.yml", "w") as f:
        yaml.dump(fleet_repos_content, f)

    env = os.environ.copy()
    env["HG_ROOT"] = str(tmp_path)

    result = run_script(env)
    assert result.returncode == 0

    output_file = tmp_path / "reports/integrity/sources.v1.json"
    with open(output_file, "r") as f:
        data = json.load(f)

    repos = [s["repo"] for s in data["sources"]]
    assert repos == ["heimgewebe/alpha-repo", "heimgewebe/beta-repo"]
