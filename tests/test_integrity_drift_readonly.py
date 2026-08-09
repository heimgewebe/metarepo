from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_integrity_sources.py"
GUARD = ROOT / "scripts" / "check-integrity-drift.sh"
BASH = shutil.which("bash")
assert BASH is not None


def _run_generator(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HG_ROOT"] = str(repo)
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _generator_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "generator-repo"
    (repo / "fleet").mkdir(parents=True)
    (repo / "fleet" / "repos.yml").write_text(
        yaml.safe_dump({"repos": ["repo1"]}),
        encoding="utf-8",
    )
    return repo


def test_generator_alternate_output_preserves_canonical_artifact(tmp_path: Path) -> None:
    repo = _generator_fixture(tmp_path)
    initial = _run_generator(repo)
    assert initial.returncode == 0, initial.stderr

    canonical = repo / "reports" / "integrity" / "sources.v1.json"
    before = canonical.read_bytes()
    candidate = tmp_path / "candidate.json"

    result = _run_generator(repo, "--output", str(candidate))

    assert result.returncode == 0, result.stderr
    assert candidate.read_bytes() == before
    assert canonical.read_bytes() == before


def _guard_fixture(
    tmp_path: Path,
    generator_body: str,
) -> tuple[Path, Path, bytes]:
    repo = tmp_path / "guard-repo"
    script = repo / "scripts" / "check-integrity-drift.sh"
    generator = repo / "scripts" / "generate_integrity_sources.py"
    report = repo / "reports" / "integrity" / "sources.v1.json"

    script.parent.mkdir(parents=True)
    report.parent.mkdir(parents=True)
    shutil.copy2(GUARD, script)
    generator.write_text(textwrap.dedent(generator_body), encoding="utf-8")

    original = b"committed integrity report\n"
    report.write_bytes(original)
    return repo, report, original


def _run_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    # Keep the fixture deterministic and exercise the portable python3 path,
    # independent of whether the development machine has uv in ~/.local/bin.
    env["PATH"] = "/usr/bin:/bin"
    return subprocess.run(
        [BASH, "scripts/check-integrity-drift.sh"],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_drift_guard_success_is_read_only(tmp_path: Path) -> None:
    repo, report, original = _guard_fixture(
        tmp_path,
        """
        import argparse
        from pathlib import Path

        parser = argparse.ArgumentParser()
        parser.add_argument("--output", required=True)
        args = parser.parse_args()
        source = Path("reports/integrity/sources.v1.json")
        Path(args.output).write_bytes(source.read_bytes())
        """,
    )

    result = _run_guard(repo)

    assert result.returncode == 0, result.stderr
    assert "Success: No drift detected." in result.stdout
    assert report.read_bytes() == original


def test_drift_guard_reports_drift_without_mutating_tracked_report(
    tmp_path: Path,
) -> None:
    repo, report, original = _guard_fixture(
        tmp_path,
        """
        import argparse
        from pathlib import Path

        parser = argparse.ArgumentParser()
        parser.add_argument("--output", required=True)
        args = parser.parse_args()
        Path(args.output).write_text("different generated report\\n", encoding="utf-8")
        """,
    )

    result = _run_guard(repo)

    assert result.returncode == 1
    assert "Drift detected" in result.stdout
    assert report.read_bytes() == original


def test_drift_guard_propagates_generator_failure_without_mutating_tracked_report(
    tmp_path: Path,
) -> None:
    repo, report, original = _guard_fixture(
        tmp_path,
        """
        import argparse
        from pathlib import Path

        parser = argparse.ArgumentParser()
        parser.add_argument("--output", required=True)
        args = parser.parse_args()
        Path(args.output).write_text("partial candidate\\n", encoding="utf-8")
        raise SystemExit(7)
        """,
    )

    result = _run_guard(repo)

    assert result.returncode == 7
    assert "Generator script failed" in result.stdout
    assert report.read_bytes() == original
