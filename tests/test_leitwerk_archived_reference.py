from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "1449145af543b78c0d3813942f1d6d95ddb33c4a"
CONTENT_SHA256 = "1cf39dc5c311d1cf8d1f91b536354b887d25e810dac215dbb60700148f09948f"
LOCATOR = "archive/leitwerk.freeze.v1.json"



def test_leitwerk_repository_identity_is_absent_from_fleet_scope() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/repos.yml").read_text(encoding="utf-8"))
    assert "leitwerk" not in [entry["name"] for entry in fleet["repos"]]
    assert "leitwerk" not in [entry["name"] for entry in fleet["static"]["include"]]


def test_leitwerk_is_absent_from_metadata_and_projection() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )
    assert "leitwerk" not in metadata["repositories"]
    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    assert "leitwerk" not in [entry["name"] for entry in projection["repos"]]
    assert projection["archived_references"] == []

def test_dispatch_hard_blocks_archived_leitwerk_even_if_allowlist_is_overridden() -> None:
    workflow = (
        ROOT / ".github/workflows/heimgewebe-command-dispatch.yml"
    ).read_text(encoding="utf-8")
    archived_repos_declaration = next(
        line for line in workflow.splitlines() if "const archivedRepos = new Set([" in line
    )
    assert '"leitwerk"' in archived_repos_declaration
    assert workflow.index("archivedRepos.has(targetRepo)") < workflow.index(
        "!allowedRepos.includes(targetRepo)"
    )



def test_generated_surfaces_do_not_project_deleted_leitwerk_repository() -> None:
    for relative in (
        "docs/repo-matrix.md",
        "docs/org-index.md",
        "docs/org-graph.mmd",
        "docs/_generated/fleet.md",
    ):
        assert "leitwerk" not in (ROOT / relative).read_text(encoding="utf-8")
