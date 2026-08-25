from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_CONFIG = ROOT / "automation" / "renovate" / "runtime-config.cjs"


def _runtime_command_matches(commands: list[str]) -> dict[str, object]:
    script = (
        "const config = require(process.argv[1]); "
        "const commands = process.argv.slice(2); "
        "const matches = commands.map((command) => "
        "config.allowedCommands.some((pattern) => new RegExp(pattern).test(command))); "
        "process.stdout.write(JSON.stringify({allowedCommands: config.allowedCommands, matches}));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(RUNTIME_CONFIG), *commands],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def test_runtime_allows_only_exact_repoground_post_upgrade_commands() -> None:
    commands = [
        "bash /home/alex/.local/share/renovate-fleet/current/automation/renovate/repoground-lock-coupling.sh",
        "python3 scripts/ci/refresh_workflow_control_plane.py",
        "python3 scripts/ci/refresh_workflow_control_plane.py --root .",
        "python scripts/ci/refresh_workflow_control_plane.py",
        "python3 ./scripts/ci/refresh_workflow_control_plane.py",
        "bash -lc 'python3 scripts/ci/refresh_workflow_control_plane.py'",
    ]

    resolved = _runtime_command_matches(commands)

    assert resolved["allowedCommands"] == [
        r"^bash /home/alex/\.local/share/renovate-fleet/current/automation/renovate/repoground-lock-coupling\.sh$",
        r"^python3 scripts/ci/refresh_workflow_control_plane\.py$",
    ]
    assert resolved["matches"] == [True, True, False, False, False, False]
