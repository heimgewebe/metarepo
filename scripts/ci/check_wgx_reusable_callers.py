#!/usr/bin/env python3
"""Validate Metarepo ownership of repository-verification workflow callers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WGX_RUNNER_REF = "03da8c71fa5bb30827a1a8e91e2a48bacaf3140c"
LOCAL_REUSABLE = "uses: ./.github/workflows/reusable-repo-verify.yml"


def check_callers(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    workflows = root / ".github" / "workflows"
    guard_path = workflows / "wgx-guard.yml"
    smoke_path = workflows / "wgx-smoke.yml"
    reusable_path = workflows / "reusable-repo-verify.yml"

    for path, mode in ((guard_path, "guard"), (smoke_path, "smoke")):
        if not path.is_file():
            findings.append(f"workflow not found: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if LOCAL_REUSABLE not in text:
            findings.append(f"{path.name} does not route through Metarepo reusable verification")
        if f"mode: {mode}" not in text:
            findings.append(f"{path.name} does not bind verification mode {mode}")
        if "heimgewebe/wgx/.github/workflows/" in text:
            findings.append(f"{path.name} still delegates workflow ownership to WGX")

    if not reusable_path.is_file():
        findings.append(f"workflow not found: {reusable_path}")
    else:
        reusable = reusable_path.read_text(encoding="utf-8")
        if "repository: heimgewebe/wgx" not in reusable:
            findings.append("reusable verification does not declare the compatibility runner")
        if f"ref: {WGX_RUNNER_REF}" not in reusable:
            findings.append("reusable verification runner is not revision-bound")
        if "heimgewebe/wgx/.github/workflows/" in reusable:
            findings.append("reusable verification delegates policy back to WGX workflows")
        for mode in ("guard", "smoke", "quick", "full"):
            if mode not in reusable:
                findings.append(f"reusable verification does not expose mode {mode}")

    return findings


def main() -> int:
    findings = check_callers()
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}", file=sys.stderr)
        return 1
    print("PASS: Metarepo owns repository-verification workflow routing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
