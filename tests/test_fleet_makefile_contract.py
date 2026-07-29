from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_makefile_uses_canonical_fleet_cli_options() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "--matrix" not in makefile
    assert "--fleet-file fleet/repos.yml" in makefile
    assert "--repos-yml repos.yml" in makefile
    assert "--source fleet/repos.yml" in makefile
    assert "repo-matrix-check:" in makefile


def test_makefile_fleet_checks_are_executable() -> None:
    subprocess.run(["make", "fleet-check"], cwd=ROOT, check=True)
    subprocess.run(["make", "repo-matrix-check"], cwd=ROOT, check=True)


def test_makefile_fleet_dry_run_preserves_new_contract() -> None:
    result = subprocess.run(
        ["make", "-n", "fleet"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "--fleet-file fleet/repos.yml" in result.stdout
    assert "--repos-yml repos.yml" in result.stdout
    assert "--matrix" not in result.stdout
