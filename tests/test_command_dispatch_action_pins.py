from pathlib import Path

from scripts.ci.check_command_dispatch_action_pins import check_workflow

ROOT = Path(__file__).resolve().parents[1]


def test_repository_command_dispatch_uses_full_commit_pins() -> None:
    assert check_workflow(
        ROOT / ".github" / "workflows" / "heimgewebe-command-dispatch.yml"
    ) == []


def test_repository_observatory_reusable_uses_full_commit_pins() -> None:
    assert check_workflow(
        ROOT / ".github" / "workflows" / "reusable-validate-observatory.yml"
    ) == []


def test_mutable_major_tag_is_rejected(tmp_path: Path) -> None:
    workflow = tmp_path / "workflow.yml"
    workflow.write_text("steps:\n  - uses: actions/github-script@v8\n", encoding="utf-8")
    assert "actions/github-script@v8 is not pinned" in check_workflow(workflow)[0]


def test_abbreviated_sha_is_rejected(tmp_path: Path) -> None:
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(
        "steps:\n  - uses: actions/create-github-app-token@bcd2ba4\n",
        encoding="utf-8",
    )
    assert "actions/create-github-app-token@bcd2ba4 is not pinned" in check_workflow(
        workflow
    )[0]


def test_quoted_local_action_is_allowed(tmp_path: Path) -> None:
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(
        "steps:\n"
        "  - uses: './local-action'\n"
        "  - uses: 'actions/github-script@3a2844b7e9c422d3c10d287c895573f7108da1b3'\n",
        encoding="utf-8",
    )
    assert check_workflow(workflow) == []
