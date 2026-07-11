#!/usr/bin/env python3
"""Reject duplicate keys and non-finite numbers in contract JSON files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _files(paths: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_dir():
            files.update(candidate for candidate in path.rglob("*.json") if candidate.is_file())
        elif path.is_file():
            files.add(path)
        else:
            raise ValueError(f"path does not exist: {path}")
    return sorted(files)


def check(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in _files(paths):
        try:
            json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=_object_without_duplicates,
                parse_constant=_reject_constant,
            )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    errors = check(args.paths)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"contract JSON strict parse: valid ({len(_files(args.paths))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
