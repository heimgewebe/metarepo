#!/usr/bin/env python3
"""Verify fleet/repos.txt against canonical fleet/repos.yml byte-for-byte."""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wgx import repo_config


def expected_content(source: Path) -> str:
    names = repo_config.active_fleet_names(repo_config.load_config(source))
    if not names:
        raise ValueError(f"No active Fleet repositories in {source}")
    return "\n".join(names) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="fleet/repos.yml")
    parser.add_argument("--fleet", default="fleet/repos.txt")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.fleet).resolve()
    expected = expected_content(source)
    actual = output.read_text(encoding="utf-8") if output.exists() else ""
    if actual == expected:
        print("✅ fleet/repos.txt matches canonical fleet/repos.yml exactly.")
        return 0
    print("❌ fleet/repos.txt does not match canonical fleet/repos.yml.")
    sys.stdout.writelines(difflib.unified_diff(
        expected.splitlines(keepends=True), actual.splitlines(keepends=True),
        fromfile="expected (fleet/repos.yml)", tofile=str(output),
    ))
    print("Fix: run `just fleet`.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
