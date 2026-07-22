from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_COMMIT = "f74579cbe46d5f5f7b95c4c3431da03efb67cc85"


def test_heimlern_is_only_an_archived_fleet_reference() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/repos.yml").read_text(encoding="utf-8"))
    assert "heimlern" not in [entry["name"] for entry in fleet["repos"]]
    archived = [
        entry
        for entry in fleet["static"]["include"]
        if entry["name"] == "heimlern"
    ]
    assert len(archived) == 1
    assert archived[0]["status"] == "archived-reference"
    assert archived[0]["fleet"] is False
    assert archived[0]["source_commit"] == ARCHIVE_COMMIT


def test_metadata_and_active_contract_consumers_do_not_project_heimlern() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )
    assert "heimlern" not in metadata["repositories"]
    meta = json.loads(
        (ROOT / "contracts/events/heimgeist.insight.v1.meta.json").read_text(
            encoding="utf-8"
        )
    )
    assert "heimlern" not in meta["governance"]["consumers"]
    registry = yaml.safe_load(
        (ROOT / "contracts/consumers.yaml").read_text(encoding="utf-8")
    )
    active_observatory_consumers = registry["knowledge"]["observatory"]["consumers"]
    assert "heimlern" not in [item["repo"] for item in active_observatory_consumers]


def test_dispatch_hard_blocks_archived_repository_even_if_variable_is_overridden() -> None:
    workflow = (
        ROOT / ".github/workflows/heimgewebe-command-dispatch.yml"
    ).read_text(encoding="utf-8")
    default_allowlist = workflow.split("ALLOWED_TARGET_REPOS:", 1)[1].split("\n", 1)[0]
    assert "heimlern" not in default_allowlist
    assert 'const archivedRepos = new Set(["heimlern"])' in workflow
    assert workflow.index("archivedRepos.has(targetRepo)") < workflow.index(
        "!allowedRepos.includes(targetRepo)"
    )


def test_retired_direct_e2e_paths_always_fail_closed(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.update(
        {
            "AUSSENSENSOR_DIR": str(tmp_path),
            "CHRONIK_INGEST_URL": "http://127.0.0.1:1/chronik",
            "CHRONIK_TOKEN": "do-not-use",
            "HEIMLERN_INGEST_URL": "http://127.0.0.1:1/heimlern",
            "DRY_RUN": "1",
            "LOG_DIR": str(tmp_path / "logs"),
        }
    )
    for relative in (
        "scripts/e2e/run_aussen_to_heimlern.sh",
        "scripts/e2e/report.sh",
    ):
        result = subprocess.run(
            ["bash", str(ROOT / relative)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 64
        assert "ARCHIVED_PATH" in result.stderr
    assert not (tmp_path / "logs").exists()


def test_active_projection_docs_do_not_describe_heimlern_as_fleet() -> None:
    matrix = (ROOT / "docs/repo-matrix.md").read_text(encoding="utf-8")
    active_section = matrix.split("## Archived References", 1)[0]
    assert "heimlern" not in active_section
    assert "Archivierte Policy- und Lernreferenz" in matrix


def test_active_ai_context_is_disabled_and_historical() -> None:
    context = yaml.safe_load(
        (ROOT / "ai-contexts/heimlern.ai-context.yml").read_text(encoding="utf-8")
    )
    assert context["project"]["role"] == "archived_reference"
    assert context["heimgewebe"]["fleet"]["enabled"] is False
    assert context["heimgewebe"]["wgx"]["profile_expected"] is False
    assert context["heimgewebe"]["wgx"]["guard_smoke_expected"] is False
    assert context["interfaces"]["produces"] == ["none (archived repository)"]


def test_integrity_pull_sources_exclude_archived_heimlern() -> None:
    sources = json.loads(
        (ROOT / "reports/integrity/sources.v1.json").read_text(encoding="utf-8")
    )["sources"]
    assert "heimgewebe/heimlern" not in [source["repo"] for source in sources]


def test_active_docs_and_rollout_surfaces_do_not_reactivate_heimlern() -> None:
    assertions = {
        "docs/policies/automation.md": "historische Kompatibilitätsnamen",
        "docs/policies/ci-reusables.md": "kein aktiver Workflow-Consumer",
        "docs/fleet/push-to-fleet.md": "dürfen nicht als Rollout-Ziel",
        ".github/ISSUE_TEMPLATE/rollout.md": "keine `archived-reference`",
        "docs/contracts/mitschreiber.md": "Historische Lernreferenz",
    }
    for relative, required_marker in assertions.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert required_marker in text
    rollout = (ROOT / ".github/ISSUE_TEMPLATE/rollout.md").read_text(
        encoding="utf-8"
    )
    assert "**heimlern**" not in rollout
