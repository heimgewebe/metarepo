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


def _fake_gh(path: Path) -> None:
    _write_executable(
        path,
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "[[ \"$*\" == \"auth token\" ]]\n"
        "printf '%s\\n' 'test-token'\n",
    )


def _fake_npx(path: Path) -> None:
    _write_executable(
        path,
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"${RENOVATE_TOKEN}\" > \"${CAPTURE_DIR}/token\"\n"
        "printf '%s\\n' \"${RENOVATE_CONFIG_FILE}\" > \"${CAPTURE_DIR}/config\"\n"
        "printf '%s\\n' \"$@\" > \"${CAPTURE_DIR}/args\"\n"
        "printf '%s\\n' \"${PATH}\" > \"${CAPTURE_DIR}/path\"\n"
        "printf '%s\\n' \"${XDG_RUNTIME_DIR}\" > \"${CAPTURE_DIR}/xdg-runtime-dir\"\n"
        "printf '%s\\n' \"${DBUS_SESSION_BUS_ADDRESS}\" > \"${CAPTURE_DIR}/dbus-address\"\n"
        "printf '%s\\n' \"${GIT_CONFIG_COUNT}\" > \"${CAPTURE_DIR}/git-config-count\"\n"
        "printf '%s\\n' \"${GIT_CONFIG_KEY_0}\" > \"${CAPTURE_DIR}/git-config-key\"\n"
        "printf '%s\\n' \"${GIT_CONFIG_VALUE_0}\" > \"${CAPTURE_DIR}/git-config-value\"\n"
        "git config --get core.hooksPath > \"${CAPTURE_DIR}/git-hooks-path\"\n",
    )


def _assert_runtime_contract(
    capture: Path, expected_path: str, expected_runtime_dir: Path
) -> None:
    assert (capture / "token").read_text(encoding="utf-8") == "test-token\n"
    assert (capture / "config").read_text(encoding="utf-8") == f"{RUNTIME_CONFIG}\n"
    assert (capture / "args").read_text(encoding="utf-8").splitlines() == [
        "--yes",
        "renovate@42.99.0",
        "--dry-run=lookup",
    ]
    assert (capture / "path").read_text(encoding="utf-8") == f"{expected_path}\n"
    assert (capture / "xdg-runtime-dir").read_text(encoding="utf-8") == f"{expected_runtime_dir}\n"
    assert (capture / "dbus-address").read_text(encoding="utf-8") == (
        f"unix:path={expected_runtime_dir}/bus\n"
    )
    assert (capture / "git-config-count").read_text(encoding="utf-8") == "1\n"
    assert (capture / "git-config-key").read_text(encoding="utf-8") == "core.hooksPath\n"
    assert (capture / "git-config-value").read_text(encoding="utf-8") == "/dev/null\n"
    assert (capture / "git-hooks-path").read_text(encoding="utf-8") == "/dev/null\n"


def test_runner_defaults_to_system_npx_and_forwards_runtime_contract(tmp_path: Path) -> None:
    runner_text = RUNNER.read_text(encoding="utf-8")
    assert 'NPX_BIN="${RENOVATE_NPX_BIN:-/usr/bin/npx}"' in runner_text
    assert 'export PATH="${RENOVATE_TOOL_PATH:-${DEFAULT_TOOL_PATH}}"' in runner_text
    assert 'export DBUS_SESSION_BUS_ADDRESS="unix:path=${RUNTIME_DIR}/bus"' in runner_text
    assert 'export GIT_CONFIG_KEY_0=core.hooksPath' in runner_text
    assert 'export GIT_CONFIG_VALUE_0=/dev/null' in runner_text
    assert 'exec "${NPX_BIN}" --yes "renovate@${RENOVATE_VERSION}" "$@"' in runner_text

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    capture = tmp_path / "capture"
    capture.mkdir()
    fake_gh = fake_bin / "gh"
    fake_npx = fake_bin / "npx-direct"
    _fake_gh(fake_gh)
    _fake_npx(fake_npx)

    custom_path = f"{fake_bin}:/usr/bin:/bin"
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    env = os.environ.copy()
    env.update(
        {
            "RENOVATE_TOOL_PATH": custom_path,
            "RENOVATE_NPX_BIN": str(fake_npx),
            "RENOVATE_XDG_RUNTIME_DIR": str(runtime_dir),
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

    _assert_runtime_contract(capture, custom_path, runtime_dir)


def test_runner_supplies_user_tools_in_systemd_environment(tmp_path: Path) -> None:
    home = tmp_path / "home"
    cargo_bin = home / ".cargo" / "bin"
    local_bin = home / ".local" / "bin"
    bun_bin = home / ".bun" / "bin"
    cargo_bin.mkdir(parents=True)
    local_bin.mkdir(parents=True)
    capture = tmp_path / "capture"
    capture.mkdir()
    fake_npx = tmp_path / "npx-direct"
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    _fake_gh(local_bin / "gh")
    _fake_npx(fake_npx)

    env = os.environ.copy()
    env.pop("RENOVATE_TOOL_PATH", None)
    env.update(
        {
            "HOME": str(home),
            "PATH": "/usr/bin:/bin",
            "RENOVATE_NPX_BIN": str(fake_npx),
            "RENOVATE_XDG_RUNTIME_DIR": str(runtime_dir),
            "CAPTURE_DIR": str(capture),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": str(tmp_path / "host-hooks"),
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

    expected_path = f"{cargo_bin}:{local_bin}:{bun_bin}:/usr/local/bin:/usr/bin:/bin"
    _assert_runtime_contract(capture, expected_path, runtime_dir)


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
