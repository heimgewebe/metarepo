from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "a265afce24b6f7106c524da71ddd87ab51ba2e7c"
CONTENT_SHA256 = "42f5ded06265155f5d2d199673ecb4a8495b3cfa14b4d8ac939891093a0dc84a"
LOCATOR = "docs/archive-readiness.v1.json"



def test_hauski_repository_identity_is_absent_from_fleet_scope() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/repos.yml").read_text(encoding="utf-8"))
    assert "hausKI" not in [entry["name"] for entry in fleet["repos"]]
    assert "hausKI" not in [entry["name"] for entry in fleet["static"]["include"]]


def test_hauski_is_absent_from_metadata_and_projection() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )
    assert "hausKI" not in metadata["repositories"]
    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    assert "hausKI" not in [entry["name"] for entry in projection["repos"]]
    assert projection["archived_references"] == []

def test_dispatch_hard_blocks_archived_hauski_even_if_allowlist_is_overridden() -> None:
    workflow = (
        ROOT / ".github/workflows/heimgewebe-command-dispatch.yml"
    ).read_text(encoding="utf-8")
    archived_repos_declaration = next(
        line for line in workflow.splitlines() if "const archivedRepos = new Set([" in line
    )
    assert '"hauski"' in archived_repos_declaration
    assert "hausKI" not in next(
        line for line in workflow.splitlines() if "ALLOWED_TARGET_REPOS:" in line
    )
    assert workflow.index("archivedRepos.has(targetRepo)") < workflow.index(
        "!allowedRepos.includes(targetRepo)"
    )



def test_generated_surfaces_do_not_project_deleted_hauski_repository() -> None:
    for relative in (
        "docs/repo-matrix.md",
        "docs/org-index.md",
        "docs/org-graph.mmd",
        "docs/_generated/fleet.md",
    ):
        assert "hausKI" not in (ROOT / relative).read_text(encoding="utf-8")

def test_retired_hauski_is_not_an_active_integrity_source() -> None:
    sources = (ROOT / "reports/integrity/sources.v1.json").read_text(encoding="utf-8")
    assert '"repo": "heimgewebe/hausKI"' not in sources


def test_hauski_ai_context_is_historical_only() -> None:
    context = yaml.safe_load(
        (ROOT / "ai-contexts/hausKI.ai-context.yml").read_text(encoding="utf-8")
    )
    assert context["project"]["role"] == "archived_reference"
    assert context["heimgewebe"]["fleet"]["enabled"] is False
    assert context["source_binding"]["commit"] == SOURCE_COMMIT
