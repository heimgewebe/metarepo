#!/usr/bin/env python3
import pathlib
import re
import sys

# Get the absolute path to the repository root
# The script is in .github/workflows/, so we need to go up two levels
repo_root = pathlib.Path(__file__).parent.parent.parent
toolchain_file = repo_root / "toolchain.versions.yml"

if not toolchain_file.is_file():
    print("toolchain.versions.yml not found", file=sys.stderr)
    sys.exit(1)

text = toolchain_file.read_text()
# Updated regex to optionally match 'v' prefix and single/double quotes
match = re.search(r"^yq:\s*['\"]?v?([^'\"#\n]+)['\"]?", text, re.MULTILINE)
if not match:
    print("yq version missing in toolchain.versions.yml", file=sys.stderr)
    sys.exit(1)

print(match.group(1).strip())
