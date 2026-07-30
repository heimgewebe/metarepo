from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fleet" / "check_docs_drift.sh"
BASH = shutil.which("bash")
assert BASH is not None


def _fixture(tmp_path: Path, generator_body: str) -> tuple[Path, Path, bytes]:
    repo = tmp_path / "repo"
    script = repo / "scripts" / "fleet" / "check_docs_drift.sh"
    generator = repo / "scripts" / "fleet" / "generate_fleet_docs.py"
    generated = repo / "docs" / "_generated" / "fleet.md"

    script.parent.mkdir(parents=True)
    generated.parent.mkdir(parents=True)
    shutil.copy2(SCRIPT, script)

    original = b"committed fleet documentation\n"
    generated.write_bytes(original)
    generator.write_text(textwrap.dedent(generator_body), encoding="utf-8")

    return repo, generated, original


def _run_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [BASH, "scripts/fleet/check_docs_drift.sh"],
        cwd=repo,
        stdin=subprocess.DEVNULL,
        text=True,
        capture_output=True,
        check=False,
    )


def test_generator_failure_restores_partially_written_file(tmp_path: Path) -> None:
    repo, generated, original = _fixture(
        tmp_path,
        """
        from pathlib import Path

        output = Path("docs/_generated/fleet.md")
        output.write_text("partial regenerated content\\n", encoding="utf-8")
        raise SystemExit(7)
        """,
    )

    result = _run_guard(repo)

    assert result.returncode == 7
    assert generated.read_bytes() == original


def test_detected_drift_is_reported_and_restored(tmp_path: Path) -> None:
    repo, generated, original = _fixture(
        tmp_path,
        """
        from pathlib import Path

        Path("docs/_generated/fleet.md").write_text(
            "complete but different generated content\\n",
            encoding="utf-8",
        )
        """,
    )

    result = _run_guard(repo)

    assert result.returncode == 1
    assert "Drift detected" in result.stdout
    assert generated.read_bytes() == original
