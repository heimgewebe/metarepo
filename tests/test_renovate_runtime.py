from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "automation" / "renovate" / "run-fleet.sh"
RUNTIME_CONFIG = ROOT / "automation" / "renovate" / "runtime-config.cjs"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_runner_defaults_to_system_npx_and_forwards_runtime_contract(tmp_path: Path) -> None:
    runner_text = RUNNER.read_text(encoding="utf-8")
    assert 'NPX_BIN="${RENOVATE_NPX_BIN:-/usr/bin/npx}"' in runner_text
    assert 'exec "${NPX_BIN}" --yes "renovate@${RENOVATE_VERSION}" "$@"' in runner_text

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    capture = tmp_path / "capture"
    capture.mkdir()
    fake_gh = fake_bin / "gh"
    fake_npx = fake_bin / "npx-direct"

    _write_executable(
        fake_gh,
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "[[ \"$*\" == \"auth token\" ]]\n"
        "printf '%s\\n' 'test-token'\n",
    )
    _write_executable(
        fake_npx,
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"${RENOVATE_TOKEN}\" > \"${CAPTURE_DIR}/token\"\n"
        "printf '%s\\n' \"${RENOVATE_CONFIG_FILE}\" > \"${CAPTURE_DIR}/config\"\n"
        "printf '%s\\n' \"$@\" > \"${CAPTURE_DIR}/args\"\n",
    )

    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "RENOVATE_NPX_BIN": str(fake_npx),
            "CAPTURE_DIR": str(capture),
        }
    )
    subprocess.run(
        [str(RUNNER), "--dry-run=lookup"],
        check=True,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert (capture / "token").read_text(encoding="utf-8") == "test-token\n"
    assert (capture / "config").read_text(encoding="utf-8") == f"{RUNTIME_CONFIG}\n"
    assert (capture / "args").read_text(encoding="utf-8").splitlines() == [
        "--yes",
        "renovate@42.99.0",
        "--dry-run=lookup",
    ]


def test_runner_rejects_path_resolved_npx_override() -> None:
    completed = subprocess.run(
        [str(RUNNER), "--dry-run=lookup"],
        cwd=ROOT,
        env={**os.environ, "RENOVATE_NPX_BIN": "npx"},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "must name an executable absolute path" in completed.stderr
