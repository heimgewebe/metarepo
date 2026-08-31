from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "automation" / "renovate" / "repoground-lock-coupling.sh"
RUNTIME_CONFIG = ROOT / "automation" / "renovate" / "runtime-config.cjs"
EXPECTED_COMMAND = (
    "bash /home/alex/.local/share/renovate-fleet/current/automation/renovate/"
    "repoground-lock-coupling.sh"
)


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

    (repo / "requirements-dev.txt").write_text("ruff==0.16.3\n", encoding="utf-8")
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    generator = repo / "scripts" / "release" / "compile_dependency_locks.sh"
    generator.parent.mkdir(parents=True)
    generator.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"${1:-generate}\" >> \"${CALLS_FILE:?}\"\n"
        "if [[ \"${FAIL_GENERATE:-0}\" == 1 && $# -eq 0 ]]; then exit 17; fi\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "baseline")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


def _run(repo: Path, calls: Path, **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CALLS_FILE": str(calls), **extra_env}
    return subprocess.run(
        ["bash", str(WRAPPER)],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _change_requirement(repo: Path) -> None:
    (repo / "requirements-dev.txt").write_text("ruff==0.16.4\n", encoding="utf-8")


def test_runtime_keeps_exact_repoground_lock_coupling_command() -> None:
    completed = subprocess.run(
        [
            "node",
            "-e",
            "const c=require(process.argv[1]); process.stdout.write(JSON.stringify(c.allowedCommands));",
            str(RUNTIME_CONFIG),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    patterns = json.loads(completed.stdout)
    expected_pattern = (
        "^bash /home/alex/\\.local/share/renovate-fleet/current/automation/renovate/"
        "repoground-lock-coupling\\.sh$"
    )
    assert expected_pattern in patterns
    assert __import__("re").fullmatch(expected_pattern, EXPECTED_COMMAND)


def test_committed_requirement_update_runs_generator_on_existing_branch(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    _change_requirement(repo)
    _git(repo, "add", "requirements-dev.txt")
    _git(repo, "commit", "-m", "renovate dependency update")

    completed = _run(repo, calls)

    assert completed.returncode == 0, completed.stderr
    assert calls.read_text(encoding="utf-8").splitlines() == ["generate", "--check"]


def test_uncommitted_requirement_update_runs_generator(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    _change_requirement(repo)
    _git(repo, "add", "requirements-dev.txt")

    completed = _run(repo, calls)

    assert completed.returncode == 0, completed.stderr
    assert calls.read_text(encoding="utf-8").splitlines() == ["generate", "--check"]


def test_unrelated_committed_update_does_not_run_lock_generator(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "unrelated update")

    completed = _run(repo, calls)

    assert completed.returncode == 0, completed.stderr
    assert not calls.exists()
    assert "no Python requirement change on branch" in completed.stdout


def test_missing_origin_main_regenerates_fail_safe(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")

    completed = _run(repo, calls)

    assert completed.returncode == 0, completed.stderr
    assert calls.read_text(encoding="utf-8").splitlines() == ["generate", "--check"]
    assert "origin/main unavailable" in completed.stderr


def test_generator_failure_stops_before_read_only_check(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    _change_requirement(repo)

    completed = _run(repo, calls, FAIL_GENERATE="1")

    assert completed.returncode == 17
    assert calls.read_text(encoding="utf-8").splitlines() == ["generate"]


def test_missing_canonical_generator_fails_closed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    calls = tmp_path / "calls"
    _change_requirement(repo)
    (repo / "scripts" / "release" / "compile_dependency_locks.sh").unlink()

    completed = _run(repo, calls)

    assert completed.returncode == 2
    assert not calls.exists()
    assert "canonical generator is missing" in completed.stderr


def test_non_repoground_repository_is_rejected_before_repository_code_runs(tmp_path: Path) -> None:
    repo = _repo(tmp_path, origin="https://github.com/heimgewebe/audio.git")
    calls = tmp_path / "calls"
    _change_requirement(repo)

    completed = _run(repo, calls)

    assert completed.returncode == 2
    assert not calls.exists()
    assert "not heimgewebe/repoground" in completed.stderr
