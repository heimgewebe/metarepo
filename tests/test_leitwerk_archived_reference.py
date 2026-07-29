from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "1449145af543b78c0d3813942f1d6d95ddb33c4a"
CONTENT_SHA256 = "1cf39dc5c311d1cf8d1f91b536354b887d25e810dac215dbb60700148f09948f"
LOCATOR = "archive/leitwerk.freeze.v1.json"


def test_leitwerk_is_exactly_one_archived_non_fleet_reference() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/repos.yml").read_text(encoding="utf-8"))
    assert "leitwerk" not in [entry["name"] for entry in fleet["repos"]]
    entries = [
        entry
        for entry in fleet["static"]["include"]
        if entry["name"] == "leitwerk"
    ]
    assert entries == [
        {
            "name": "leitwerk",
            "url": "https://github.com/heimgewebe/leitwerk",
            "status": "archived-reference",
            "fleet": False,
            "default_branch": "main",
            "source_commit": SOURCE_COMMIT,
            "locator": LOCATOR,
            "content_sha256": CONTENT_SHA256,
        }
    ]


def test_leitwerk_is_absent_from_active_metadata_and_projection() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )
    assert "leitwerk" not in metadata["repositories"]

    projection = yaml.safe_load((ROOT / "repos.yml").read_text(encoding="utf-8"))
    assert "leitwerk" not in [entry["name"] for entry in projection["repos"]]
    archived = [
        entry
        for entry in projection["archived_references"]
        if entry["name"] == "leitwerk"
    ]
    assert len(archived) == 1
    assert archived[0]["source_commit"] == SOURCE_COMMIT
    assert archived[0]["locator"] == LOCATOR
    assert archived[0]["content_sha256"] == CONTENT_SHA256


def test_dispatch_hard_blocks_archived_leitwerk_even_if_allowlist_is_overridden() -> None:
    workflow = (
        ROOT / ".github/workflows/heimgewebe-command-dispatch.yml"
    ).read_text(encoding="utf-8")
    assert 'const archivedRepos = new Set(["heimlern", "leitwerk"])' in workflow
    assert workflow.index("archivedRepos.has(targetRepo)") < workflow.index(
        "!allowedRepos.includes(targetRepo)"
    )


def test_generated_surfaces_present_leitwerk_only_as_archived_reference() -> None:
    matrix = (ROOT / "docs/repo-matrix.md").read_text(encoding="utf-8")
    assert "| leitwerk | Archivierte Referenz; keine aktive Betriebs- oder Entwicklungsautorität | no |" in matrix

    index = (ROOT / "docs/org-index.md").read_text(encoding="utf-8")
    assert (
        "| [leitwerk](https://github.com/heimgewebe/leitwerk) | archived-reference | "
        f"`{SOURCE_COMMIT}` | `{LOCATOR}` |"
    ) in index

    graph = (ROOT / "docs/org-graph.mmd").read_text(encoding="utf-8")
    assert 'archived_leitwerk["leitwerk\\n(archived-reference; non-operational)"]' in graph

    fleet_doc = (ROOT / "docs/_generated/fleet.md").read_text(encoding="utf-8")
    assert "**leitwerk** (archived-reference) (Non-Fleet)" in fleet_doc
