from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fleet" / "generate_readiness.py"
REPOS_TXT = ROOT / "fleet" / "repos.txt"
READINESS_WORKFLOW = ROOT / ".github" / "workflows" / "readiness.yml"
DOCTOR_WORKFLOW = ROOT / ".github" / "workflows" / "fleet-doctor.yml"
MAKEFILE = ROOT / "Makefile"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_default_readiness_generation_does_not_rewrite_repos_txt(tmp_path: Path) -> None:
    before = REPOS_TXT.read_bytes()
    report = tmp_path / "readiness.json"

    result = _run("--out-json", str(report))

    assert result.returncode == 0, result.stdout + result.stderr
    assert report.exists()
    assert REPOS_TXT.read_bytes() == before


def test_explicit_repos_txt_generation_remains_supported(tmp_path: Path) -> None:
    report = tmp_path / "readiness.json"
    projection = tmp_path / "repos.txt"

    result = _run(
        "--out-json",
        str(report),
        "--write-repos-txt",
        str(projection),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert projection.read_bytes() == REPOS_TXT.read_bytes()


def test_ci_readiness_paths_are_report_only_and_fleet_generation_is_explicit() -> None:
    readiness_workflow = READINESS_WORKFLOW.read_text(encoding="utf-8")
    doctor_workflow = DOCTOR_WORKFLOW.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")

    assert "--out-json reports/heimgewebe-readiness.json" in readiness_workflow
    assert "--write-repos-txt" not in readiness_workflow
    assert "--out-json reports/heimgewebe-readiness.json" in doctor_workflow
    assert "--write-repos-txt" not in doctor_workflow
    assert "--write-repos-txt fleet/repos.txt" in makefile
