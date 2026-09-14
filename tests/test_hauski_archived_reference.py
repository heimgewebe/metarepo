from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "a265afce24b6f7106c524da71ddd87ab51ba2e7c"
CONTENT_SHA256 = "42f5ded06265155f5d2d199673ecb4a8495b3cfa14b4d8ac939891093a0dc84a"
LOCATOR = "docs/archive-readiness.v1.json"


def test_hauski_is_exactly_one_archived_non_fleet_reference() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/repos.yml").read_text(encoding="utf-8"))
    assert "hausKI" not in [entry["name"] for entry in fleet["repos"]]
    entries = [
        entry
        for entry in fleet["static"]["include"]
        if entry["name"] == "hausKI"
    ]
    assert entries == [
        {
            "name": "hausKI",
            "url": "https://github.com/heimgewebe/hausKI",
            "status": "archived-reference",
            "fleet": False,
            "default_branch": "main",
            "source_commit": SOURCE_COMMIT,
            "locator": LOCATOR,
            "content_sha256": CONTENT_SHA256,
        }
    ]


def test_hauski_is_absent_from_active_metadata_and_projection() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )
    assert "hausKI" not in metadata["repositories"]

    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    assert "hausKI" not in [entry["name"] for entry in projection["repos"]]
    archived = [
        entry
        for entry in projection["archived_references"]
        if entry["name"] == "hausKI"
    ]
    assert len(archived) == 1
    assert archived[0]["source_commit"] == SOURCE_COMMIT
    assert archived[0]["locator"] == LOCATOR
    assert archived[0]["content_sha256"] == CONTENT_SHA256


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


def test_generated_surfaces_present_hauski_only_as_archived_reference() -> None:
    matrix = (ROOT / "docs/repo-matrix.md").read_text(encoding="utf-8")
    assert "| hausKI | Archivierte Referenz; keine aktive Betriebs- oder Entwicklungsautorität | no |" in matrix
    assert "| hausKI | assistant / policy | yes |" not in matrix

    index = (ROOT / "docs/org-index.md").read_text(encoding="utf-8")
    assert (
        "| [hausKI](https://github.com/heimgewebe/hausKI) | archived-reference | "
        f"`{SOURCE_COMMIT}` | `{LOCATOR}` |"
    ) in index

    graph = (ROOT / "docs/org-graph.mmd").read_text(encoding="utf-8")
    assert 'archived_hausKI["hausKI\\n(archived-reference; non-operational)"]' in graph

    fleet_doc = (ROOT / "docs/_generated/fleet.md").read_text(encoding="utf-8")
    assert "**hausKI** (archived-reference) (Non-Fleet)" in fleet_doc


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
