from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_org_assets.py"
REPOS = ROOT / "repos.yml"
INDEX = ROOT / "docs" / "org-index.md"
GRAPH = ROOT / "docs" / "org-graph.mmd"
WORKFLOW = ROOT / ".github" / "workflows" / "org-assets.yml"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_check_mode_accepts_current_assets_without_mutation() -> None:
    index_before = INDEX.read_bytes()
    graph_before = GRAPH.read_bytes()

    result = _run(
        "--repos-file",
        str(REPOS),
        "--index",
        str(INDEX),
        "--graph",
        str(GRAPH),
        "--check",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "org assets: PASS" in result.stdout
    assert INDEX.read_bytes() == index_before
    assert GRAPH.read_bytes() == graph_before


def test_check_mode_reports_drift_without_mutation(tmp_path: Path) -> None:
    index = tmp_path / "org-index.md"
    graph = tmp_path / "org-graph.mmd"
    index.write_bytes(INDEX.read_bytes() + b"unexpected drift\n")
    graph.write_bytes(GRAPH.read_bytes())
    index_before = index.read_bytes()
    graph_before = graph.read_bytes()

    result = _run(
        "--repos-file",
        str(REPOS),
        "--index",
        str(index),
        "--graph",
        str(graph),
        "--check",
    )

    assert result.returncode == 1
    assert str(index) in result.stdout
    assert "generated" in result.stdout
    assert index.read_bytes() == index_before
    assert graph.read_bytes() == graph_before


def test_check_mode_reports_missing_output_without_creating_it(tmp_path: Path) -> None:
    index = tmp_path / "org-index.md"
    graph = tmp_path / "missing-org-graph.mmd"
    index.write_bytes(INDEX.read_bytes())
    index_before = index.read_bytes()

    result = _run(
        "--repos-file",
        str(REPOS),
        "--index",
        str(index),
        "--graph",
        str(graph),
        "--check",
    )

    assert result.returncode == 1
    assert str(graph) in result.stdout
    assert index.read_bytes() == index_before
    assert not graph.exists()


def test_generation_mode_still_writes_requested_outputs(tmp_path: Path) -> None:
    index = tmp_path / "nested" / "org-index.md"
    graph = tmp_path / "nested" / "org-graph.mmd"

    result = _run(
        "--repos-file",
        str(REPOS),
        "--index",
        str(index),
        "--graph",
        str(graph),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert index.read_bytes() == INDEX.read_bytes()
    assert graph.read_bytes() == GRAPH.read_bytes()


def test_org_assets_workflow_uses_read_only_check_mode() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "--check" in workflow
    assert "git diff --exit-code" not in workflow
    assert "git add -N" not in workflow
