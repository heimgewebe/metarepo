from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "automation" / "renovate" / "repoground-workflow-refresh.sh"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def _repo(tmp_path: Path, *, origin: str = "https://github.com/heimgewebe/repoground.git") -> Path:
    repo = tmp_path / "repoground"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "test")
    _git(repo, "remote", "add", "origin", origin)

    refresh = repo / "scripts" / "ci" / "refresh_workflow_control_plane.py"
    refresh.parent.mkdir(parents=True)
    refresh.write_text(
        "from pathlib import Path\n"
        "import os\n"
        "Path(os.environ['CALLS_FILE']).write_text('refresh\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "baseline")
    return repo


def _run(repo: Path, calls: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CALLS_FILE": str(calls)}
    return subprocess.run(
        ["bash", str(WRAPPER)],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_repoground_repository_runs_canonical_workflow_refresh(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"

    completed = _run(repo, calls)

    assert completed.returncode == 0, completed.stderr
    assert calls.read_text(encoding="utf-8") == "refresh\n"


def test_non_repoground_repository_is_rejected_before_repository_code_runs(tmp_path: Path) -> None:
    repo = _repo(tmp_path, origin="https://github.com/heimgewebe/audio.git")
    calls = tmp_path / "calls"

    completed = _run(repo, calls)

    assert completed.returncode == 2
    assert not calls.exists()
    assert "not heimgewebe/repoground" in completed.stderr


def test_missing_canonical_refresh_script_fails_closed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    (repo / "scripts" / "ci" / "refresh_workflow_control_plane.py").unlink()

    completed = _run(repo, calls)

    assert completed.returncode == 2
    assert not calls.exists()
    assert "canonical refresh script is missing" in completed.stderr
