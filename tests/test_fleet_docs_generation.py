from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/fleet/generate_fleet_docs.py"
GUARD = ROOT / "scripts/fleet/check_docs_drift.sh"


def _fixture(tmp_path: Path) -> Path:
    (tmp_path / "scripts/fleet").mkdir(parents=True)
    (tmp_path / "fleet").mkdir()
    (tmp_path / "docs/_generated").mkdir(parents=True)
    shutil.copy2(GENERATOR, tmp_path / "scripts/fleet/generate_fleet_docs.py")
    shutil.copy2(GUARD, tmp_path / "scripts/fleet/check_docs_drift.sh")
    shutil.copy2(ROOT / "fleet/repos.yml", tmp_path / "fleet/repos.yml")
    return tmp_path


def _generate(worktree: Path) -> bytes:
    result = subprocess.run(
        ["python3", "scripts/fleet/generate_fleet_docs.py"],
        cwd=worktree,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return (worktree / "docs/_generated/fleet.md").read_bytes()


def test_generated_fleet_docs_are_reproducible_and_source_bound(tmp_path: Path) -> None:
    worktree = _fixture(tmp_path)
    first = _generate(worktree)
    second = _generate(worktree)
    assert first == second
    source_hash = hashlib.sha256((worktree / "fleet/repos.yml").read_bytes()).hexdigest()
    assert f"<!-- Source SHA-256: {source_hash} -->".encode() in first
    assert b"Generated at:" not in first


def test_docs_drift_guard_rejects_and_preserves_stale_content(tmp_path: Path) -> None:
    worktree = _fixture(tmp_path)
    generated = _generate(worktree)
    stale = generated + b"unexpected drift\n"
    generated_path = worktree / "docs/_generated/fleet.md"
    generated_path.write_bytes(stale)

    result = subprocess.run(
        ["bash", "scripts/fleet/check_docs_drift.sh"],
        cwd=worktree,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Drift detected" in result.stdout
    assert generated_path.read_bytes() == stale


def test_archived_reference_remains_non_fleet_in_generated_docs(tmp_path: Path) -> None:
    worktree = _fixture(tmp_path)
    output = _generate(worktree).decode("utf-8")
    fleet = yaml.safe_load((worktree / "fleet/repos.yml").read_text(encoding="utf-8"))
    archived = next(
        item for item in fleet["static"]["include"] if item["name"] == "heimlern"
    )
    assert archived["fleet"] is False
    assert "**heimlern** (archived-reference) (Non-Fleet)" in output
