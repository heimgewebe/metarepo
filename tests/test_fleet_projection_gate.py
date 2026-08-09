from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "fleet" / "verify_generated_repos_txt.py"
GENERATED_WORKFLOW = ROOT / ".github" / "workflows" / "fleet-generated-check.yml"
LEGACY_WORKFLOW = ROOT / ".github" / "workflows" / "fleet-drift-check.yml"
LEGACY_CHECKER = ROOT / "scripts" / "fleet" / "check_fleet_list.py"


def _run(source: Path, fleet: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFY),
            "--source",
            str(source),
            "--fleet",
            str(fleet),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_strict_verifier_accepts_exact_projection(tmp_path: Path) -> None:
    source = tmp_path / "repos.yml"
    fleet = tmp_path / "repos.txt"
    source.write_text("repos:\n  - name: alpha\n  - name: beta\n", encoding="utf-8")
    fleet.write_text("alpha\nbeta\n", encoding="utf-8")

    result = _run(source, fleet)

    assert result.returncode == 0, result.stdout + result.stderr


def test_strict_verifier_rejects_semantically_equivalent_extra_bytes(
    tmp_path: Path,
) -> None:
    source = tmp_path / "repos.yml"
    fleet = tmp_path / "repos.txt"
    source.write_text("repos:\n  - name: alpha\n  - name: beta\n", encoding="utf-8")
    fleet.write_text("alpha\n# redundant comment\nbeta\n", encoding="utf-8")
    before = fleet.read_bytes()

    result = _run(source, fleet)

    assert result.returncode == 1
    assert "does not match" in result.stdout
    assert fleet.read_bytes() == before


def test_fleet_projection_has_one_authoritative_ci_gate() -> None:
    workflow = GENERATED_WORKFLOW.read_text(encoding="utf-8")

    assert "verify_generated_repos_txt.py" in workflow
    assert "generate_repo_matrix.py --check" in workflow
    assert not LEGACY_WORKFLOW.exists()
    assert not LEGACY_CHECKER.exists()
