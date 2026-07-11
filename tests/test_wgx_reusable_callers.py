from pathlib import Path

from scripts.ci.check_wgx_reusable_callers import check_callers

ROOT = Path(__file__).resolve().parents[1]


def test_repository_wgx_callers_match_declared_contracts() -> None:
    assert check_callers(ROOT) == []


def test_undeclared_input_is_rejected(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "wgx-guard.yml").write_text(
        "uses: heimgewebe/wgx/.github/workflows/wgx-guard.yml@"
        "3d823f9d26be276eef97742335dee857a64e1715\n"
        "with:\n  toolchain: stable\n",
        encoding="utf-8",
    )
    (workflows / "wgx-smoke.yml").write_text(
        "# This is the last WGX commit where wgx-smoke declares workflow_call.\n"
        "uses: heimgewebe/wgx/.github/workflows/wgx-smoke.yml@"
        "52a12ff97c402d1aa718d534a84b0225e7718c82\n",
        encoding="utf-8",
    )
    assert "wgx-guard caller passes undeclared input toolchain" in check_callers(tmp_path)


def test_unverified_guard_revision_is_rejected(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "wgx-guard.yml").write_text(
        "uses: heimgewebe/wgx/.github/workflows/wgx-guard.yml@main\n",
        encoding="utf-8",
    )
    (workflows / "wgx-smoke.yml").write_text(
        "# This is the last WGX commit where wgx-smoke declares workflow_call.\n"
        "uses: heimgewebe/wgx/.github/workflows/wgx-smoke.yml@"
        "52a12ff97c402d1aa718d534a84b0225e7718c82\n",
        encoding="utf-8",
    )
    assert "wgx-guard caller is not bound to the verified WGX merge" in check_callers(
        tmp_path
    )
