from pathlib import Path

from scripts.ci.check_wgx_reusable_callers import WGX_RUNNER_REF, check_callers

ROOT = Path(__file__).resolve().parents[1]
METAREPO_VERIFY_REF = "65db582ee20fe77c49cc052be14b4fe3349eed57"
METAREPO_VERIFY_USES = (
    "uses: heimgewebe/metarepo/.github/workflows/reusable-repo-verify.yml@"
    f"{METAREPO_VERIFY_REF}"
)


def _write_workflows(root: Path, *, guard: str, smoke: str, reusable: str) -> None:
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "wgx-guard.yml").write_text(guard, encoding="utf-8")
    (workflows / "wgx-smoke.yml").write_text(smoke, encoding="utf-8")
    (workflows / "reusable-repo-verify.yml").write_text(reusable, encoding="utf-8")


def _good_reusable() -> str:
    return (
        "guard smoke quick full\n"
        "repository: heimgewebe/wgx\n"
        f"ref: {WGX_RUNNER_REF}\n"
    )


def test_repository_wgx_callers_match_declared_contracts() -> None:
    assert check_callers(ROOT) == []


def test_metarepo_templates_do_not_reintroduce_wgx_workflow_ownership() -> None:
    templates = ROOT / "templates" / ".github" / "workflows"
    for filename, mode in (("wgx-guard.yml", "guard"), ("wgx-smoke.yml", "smoke")):
        text = (templates / filename).read_text(encoding="utf-8")
        assert METAREPO_VERIFY_USES in text
        assert f"mode: {mode}" in text
        assert "heimgewebe/wgx/.github/workflows/" not in text
        assert "@main" not in text


def test_metarepo_smoke_template_self_triggers_workflow_changes() -> None:
    smoke = (
        ROOT / "templates" / ".github" / "workflows" / "wgx-smoke.yml"
    ).read_text(encoding="utf-8")
    assert '- ".github/workflows/wgx-smoke.yml"' in smoke


def test_direct_wgx_workflow_ownership_is_rejected(tmp_path: Path) -> None:
    _write_workflows(
        tmp_path,
        guard=(
            "uses: heimgewebe/wgx/.github/workflows/wgx-guard.yml@main\n"
            "mode: guard\n"
        ),
        smoke=(
            "uses: ./.github/workflows/reusable-repo-verify.yml\n"
            "mode: smoke\n"
        ),
        reusable=_good_reusable(),
    )
    findings = check_callers(tmp_path)
    assert "wgx-guard.yml does not route through Metarepo reusable verification" in findings
    assert "wgx-guard.yml still delegates workflow ownership to WGX" in findings


def test_missing_bound_mode_is_rejected(tmp_path: Path) -> None:
    _write_workflows(
        tmp_path,
        guard="uses: ./.github/workflows/reusable-repo-verify.yml\n",
        smoke=(
            "uses: ./.github/workflows/reusable-repo-verify.yml\n"
            "mode: smoke\n"
        ),
        reusable=_good_reusable(),
    )
    assert "wgx-guard.yml does not bind verification mode guard" in check_callers(tmp_path)


def test_moving_runner_ref_is_rejected(tmp_path: Path) -> None:
    _write_workflows(
        tmp_path,
        guard=(
            "uses: ./.github/workflows/reusable-repo-verify.yml\n"
            "mode: guard\n"
        ),
        smoke=(
            "uses: ./.github/workflows/reusable-repo-verify.yml\n"
            "mode: smoke\n"
        ),
        reusable=(
            "guard smoke quick full\n"
            "repository: heimgewebe/wgx\n"
            "ref: main\n"
        ),
    )
    assert "reusable verification runner is not revision-bound" in check_callers(tmp_path)
