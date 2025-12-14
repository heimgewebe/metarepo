#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def patch_post_create(cmd: str) -> str:
    """
    Insert a call to .devcontainer/setup-wgx-bridge.sh into postCreateCommand.
    We keep this conservative: only patch if we find `.devcontainer/setup.sh`
    and we don't already mention setup-wgx-bridge.
    """
    if "setup-wgx-bridge.sh" in cmd:
        return cmd
    needle = ".devcontainer/setup.sh"
    if needle not in cmd:
        return cmd

    # Common patterns:
    # 1) ".devcontainer/setup.sh && ..."
    # 2) "bash -lc '.devcontainer/setup.sh ...'"
    # We insert right after first occurrence of setup.sh invocation.
    return cmd.replace(needle, needle + " && .devcontainer/setup-wgx-bridge.sh", 1)

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: _wgx-bridge-patch-devcontainer-json.py <path-to-devcontainer.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))

    cmd = data.get("postCreateCommand")
    if not isinstance(cmd, str) or not cmd.strip():
        return 0

    patched = patch_post_create(cmd)
    if patched == cmd:
        return 0

    data["postCreateCommand"] = patched
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
