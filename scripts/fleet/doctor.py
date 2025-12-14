#!/usr/bin/env python3
"""
hg-doctor — Fleet coherence diagnostics
"""

import json
import sys
from pathlib import Path


def main() -> int:
    report = Path("reports/heimgewebe-readiness.json")
    if not report.exists():
        print("❌ missing readiness report")
        return 3

    data = json.loads(report.read_text())
    repos = data.get("repos", [])

    missing_repo = [r["name"] for r in repos if r["missing_repo"]]
    missing_decl = [r["name"] for r in repos if r["wgx_profile_kind"] == "missing"]
    no_profile = [r["name"] for r in repos if r["wgx_profile_kind"] == "no_profile"]

    print("hg-doctor")
    print("---------")

    if no_profile:
        print("Observer repos (NO_PROFILE):")
        for r in no_profile:
            print("  -", r)

    if missing_decl:
        print("❌ Missing WGX declaration:")
        for r in missing_decl:
            print("  -", r)

    if missing_repo:
        print("❌ Missing repos:")
        for r in missing_repo:
            print("  -", r)

    if missing_repo or missing_decl:
        return 3

    print("✅ Fleet coherent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
