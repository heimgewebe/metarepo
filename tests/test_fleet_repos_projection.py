from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from wgx import repo_config


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fleet" / "generate_repos_projection.py"
PROJECTION_SEMANTIC_SHA256 = "17681403a785f75c270dbf51e26c8fd1ade1d76dcd7cf042d247252c5edbfaaf"
SPEC = importlib.util.spec_from_file_location("generate_repos_projection", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

ProjectionError = MODULE.ProjectionError
build_projection = MODULE.build_projection
expected_projection = MODULE.expected_projection


def test_repository_projection_is_current() -> None:
    expected = expected_projection(
        ROOT / "fleet" / "repos.yml",
        ROOT / "fleet" / "repo-metadata.yml",
    )
    assert (ROOT / "repos.yml").read_text(encoding="utf-8") == expected


def test_projection_is_loadable_by_existing_legacy_consumers() -> None:
    projection = repo_config.load_config(ROOT / "repos.yml")

    assert projection["mode"] == "static"
    assert projection["github"]["owner"] == "heimgewebe"
    assert len(projection["repos"]) == 10
    assert [item["name"] for item in projection["archived_references"]] == ["heimlern"]


def test_projection_pins_complete_compatibility_semantics() -> None:
    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    assert hashlib.sha256(canonical).hexdigest() == PROJECTION_SEMANTIC_SHA256


def test_projection_preserves_legacy_consumer_shape() -> None:
    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))

    assert projection["mode"] == "static"
    assert projection["github"]["owner"] == "heimgewebe"
    names = [item["name"] for item in projection["repos"]]
    assert names == [
        "contracts-mirror",
        "weltgewebe",
        "hausKI",
        "hausKI-audio",
        "semantAH",
        "wgx",
        "repoground",
        "chronik",
        "aussensensor",
        "vault-gewebe",
    ]
    assert all(
        item["url"].startswith("https://github.com/heimgewebe/")
        for item in projection["repos"]
    )


def test_metadata_must_reference_projectable_fleet_or_related_repo() -> None:
    fleet = {"repos": [{"name": "known"}]}
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "unknown": {"default_branch": "main"},
        },
    }

    with pytest.raises(ProjectionError, match="not projectable"):
        build_projection(fleet, metadata)


def test_related_repository_metadata_is_allowed() -> None:
    fleet = {
        "static": {"include": [{"name": "related", "status": "related"}]},
        "repos": [{"name": "core"}],
    }
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "related": {"default_branch": "main"},
        },
    }

    projection = build_projection(fleet, metadata)
    assert projection["repos"] == [
        {
            "name": "related",
            "url": "https://github.com/example/related",
            "default_branch": "main",
        }
    ]


def test_fleet_false_related_repository_cannot_be_projected() -> None:
    fleet = {
        "static": {"include": [{"name": "private", "fleet": False}]},
        "repos": [{"name": "core"}],
    }
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "private": {"default_branch": "main"},
        },
    }

    with pytest.raises(ProjectionError, match="not projectable"):
        build_projection(fleet, metadata)


def test_fleet_false_primary_repository_cannot_be_projected() -> None:
    fleet = {
        "repos": [
            {"name": "core"},
            {"name": "private", "fleet": False},
        ]
    }
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "private": {"default_branch": "main"},
        },
    }

    with pytest.raises(ProjectionError, match="not projectable"):
        build_projection(fleet, metadata)


def test_fleet_flag_must_be_boolean() -> None:
    fleet = {
        "static": {"include": [{"name": "related", "fleet": "no"}]},
        "repos": [{"name": "core"}],
    }
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {"core": {"default_branch": "main"}},
    }

    with pytest.raises(ProjectionError, match="fleet must be boolean"):
        build_projection(fleet, metadata)


def test_normalized_metadata_names_must_be_unique() -> None:
    fleet = {"repos": [{"name": "core"}]}
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "core": {"default_branch": "main"},
            " core ": {"default_branch": "main"},
        },
    }

    with pytest.raises(ProjectionError, match="duplicate normalized metadata"):
        build_projection(fleet, metadata)


def test_duplicate_yaml_keys_fail_closed(tmp_path: Path) -> None:
    fleet = tmp_path / "fleet.yml"
    metadata = tmp_path / "metadata.yml"
    fleet.write_text("repos:\n  - name: core\n", encoding="utf-8")
    metadata.write_text(
        "schema_version: 1\n"
        "github:\n"
        "  owner: example\n"
        "repositories:\n"
        "  core:\n"
        "    default_branch: main\n"
        "  core:\n"
        "    default_branch: trunk\n",
        encoding="utf-8",
    )

    with pytest.raises(ProjectionError, match="duplicate key 'core'"):
        expected_projection(fleet, metadata)


def test_unknown_dependency_is_rejected() -> None:
    fleet = {"repos": [{"name": "core"}]}
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "core": {
                "default_branch": "main",
                "depends_on": ["missing"],
            },
        },
    }

    with pytest.raises(ProjectionError, match="non-projectable repositories"):
        build_projection(fleet, metadata)


def test_nested_consumer_metadata_must_be_mapping() -> None:
    fleet = {"repos": [{"name": "core"}]}
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {
            "core": {"default_branch": "main", "metrics": False},
        },
    }

    with pytest.raises(ProjectionError, match="metrics must be a mapping"):
        build_projection(fleet, metadata)


def test_check_mode_fails_for_stale_projection(tmp_path: Path) -> None:
    fleet = tmp_path / "fleet.yml"
    metadata = tmp_path / "metadata.yml"
    output = tmp_path / "repos.yml"
    fleet.write_text("repos:\n  - name: core\n", encoding="utf-8")
    metadata.write_text(
        "schema_version: 1\n"
        "github:\n"
        "  owner: example\n"
        "repositories:\n"
        "  core:\n"
        "    default_branch: main\n",
        encoding="utf-8",
    )
    output.write_text("stale: true\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fleet-file",
            str(fleet),
            "--metadata-file",
            str(metadata),
            "--output",
            str(output),
            "--check",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "repos.yml is stale" in result.stderr


def test_archived_reference_is_separate_and_exactly_bound() -> None:
    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    assert projection["archived_references"] == [
        {
            "name": "heimlern",
            "url": "https://github.com/heimgewebe/heimlern",
            "status": "archived-reference",
            "fleet": False,
            "default_branch": "main",
            "source_commit": "f74579cbe46d5f5f7b95c4c3431da03efb67cc85",
            "locator": "docs/archive-readiness.v1.json",
            "content_sha256": (
                "bbf1d19865812b9584a3645ecd031f0854ee6110849d249692b4ac62d8f8d1e0"
            ),
        }
    ]
    assert "heimlern" not in [item["name"] for item in projection["repos"]]


def test_archived_reference_cannot_be_projectable() -> None:
    fleet = {
        "static": {
            "include": [
                {
                    "name": "old",
                    "status": "archived-reference",
                    "fleet": True,
                }
            ]
        },
        "repos": [{"name": "core"}],
    }
    metadata = {
        "schema_version": 1,
        "github": {"owner": "example"},
        "repositories": {"core": {"default_branch": "main"}},
    }
    with pytest.raises(ProjectionError, match="must set fleet: false"):
        build_projection(fleet, metadata)
