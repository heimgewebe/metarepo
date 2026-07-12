#!/usr/bin/env python3
"""Validate the pinned metarepo callers for reusable WGX workflows."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WGX_GUARD_MERGE = "3d823f9d26be276eef97742335dee857a64e1715"
VERIFIED_WGX_SMOKE_MERGE = "b3b358f5bb8d26f087fcdaf25d308d439b22f583"


def check_callers(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    guard_path = root / ".github" / "workflows" / "wgx-guard.yml"
    smoke_path = root / ".github" / "workflows" / "wgx-smoke.yml"

    if not guard_path.is_file():
        findings.append(f"workflow not found: {guard_path}")
    else:
        guard = guard_path.read_text(encoding="utf-8")
        expected = (
            "uses: heimgewebe/wgx/.github/workflows/wgx-guard.yml@"
            f"{WGX_GUARD_MERGE}"
        )
        if expected not in guard:
            findings.append("wgx-guard caller is not bound to the verified WGX merge")
        if "toolchain: stable" in guard:
            findings.append("wgx-guard caller passes undeclared input toolchain")

    if not smoke_path.is_file():
        findings.append(f"workflow not found: {smoke_path}")
    else:
        smoke = smoke_path.read_text(encoding="utf-8")
        expected = (
            "uses: heimgewebe/wgx/.github/workflows/wgx-smoke.yml@"
            f"{VERIFIED_WGX_SMOKE_MERGE}"
        )
        if expected not in smoke:
            findings.append("wgx-smoke caller is not bound to the verified reusable smoke merge")
        if "toolchain: stable" in smoke:
            findings.append("wgx-smoke caller passes undeclared input toolchain")
        if "verifizierten WGX-Merge mit wiederverwendbarem Smoke" not in smoke:
            findings.append("wgx-smoke caller does not document its verified contract boundary")

    return findings


def main() -> int:
    findings = check_callers()
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}", file=sys.stderr)
        return 1
    print("PASS: WGX reusable callers match their declared contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
