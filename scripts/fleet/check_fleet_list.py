#!/usr/bin/env python3
"""Check the machine-readable Fleet list against canonical membership."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wgx import repo_config


def _read(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="fleet/repos.yml")
    parser.add_argument("--fleet", default="fleet/repos.txt")
    args = parser.parse_args()
    truth = repo_config.active_fleet_names(repo_config.load_config(ROOT / args.source))
    observed = _read(ROOT / args.fleet)
    if observed == truth:
        print("✅ Fleet list matches canonical fleet/repos.yml.")
        return 0
    missing = sorted(set(truth) - set(observed))
    extra = sorted(set(observed) - set(truth))
    if missing:
        print("Missing:", ", ".join(missing))
    if extra:
        print("Extra:", ", ".join(extra))
    if not missing and not extra:
        print("Order differs from canonical declaration order.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
