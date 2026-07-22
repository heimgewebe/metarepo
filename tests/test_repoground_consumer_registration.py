from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_active_fleet_surfaces_use_repoground_identity() -> None:
    active_paths = (
        "fleet/repos.yml",
        "fleet/repo-metadata.yml",
        "repos.yml",
        "docs/org-index.md",
        "docs/org-graph.mmd",
        "docs/nutzung.md",
        "reports/integrity/sources.v1.json",
        "ai-contexts/repoground.ai-context.yml",
    )

    for relative_path in active_paths:
        text = _read(relative_path)
        assert "repoground" in text.lower(), relative_path
        assert "heimgewebe/lenskit" not in text, relative_path

    assert not (ROOT / "ai-contexts" / "lenskit.ai-context.yml").exists()


def test_dispatch_keeps_legacy_aliases_but_targets_repoground() -> None:
    workflow = _read(".github/workflows/heimgewebe-command-dispatch.yml")

    assert "leitstand,repoground" in workflow
    assert '["tools", "lenskit"].includes(targetRepo)' in workflow
    assert "Bitte nutze **repoground**" in workflow
    assert "leitstand,lenskit" not in workflow


def test_repo_identity_guard_does_not_require_pcre2() -> None:
    guard = _read("scripts/fleet/check_docs_drift.sh")

    assert "LEGACY_PATTERN_RG=" in guard
    assert '"$LEGACY_PATTERN_RG" .' in guard
    assert "--glob '!tests/**'" in guard
    assert "--exclude-dir='tests'" in guard
    assert "--pcre2" not in guard
