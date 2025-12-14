#!/usr/bin/env python3
"""
hg-doctor — Fleet coherence diagnostics
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Fleet coherence diagnostics")
    ap.add_argument("--report", default="reports/heimgewebe-readiness.json",
                    help="Path to readiness report JSON")
    ap.add_argument("--ci", action="store_true",
                    help="CI mode (only validate report structure, not fleet state)")
    args = ap.parse_args()

    report = Path(args.report)
    
    try:
        if not report.exists():
            print(f"❌ missing readiness report: {report}", file=sys.stderr)
            return 3

        data = json.loads(report.read_text())
        repos = data.get("repos", [])

        # Validate report structure
        if not isinstance(repos, list):
            print("❌ Invalid report structure: 'repos' must be a list", file=sys.stderr)
            return 3
        
        if "generated_at" not in data:
            print("❌ Invalid report structure: missing 'generated_at'", file=sys.stderr)
            return 3

        missing_repo = [r["name"] for r in repos if r["missing_repo"]]
        missing_decl = [r["name"] for r in repos if r["wgx_profile_kind"] == "missing"]
        no_profile = [r["name"] for r in repos if r["wgx_profile_kind"] == "no_profile"]

        print("hg-doctor")
        print("---------")
        
        if args.ci:
            # In CI mode, only validate report generation, not fleet state
            print(f"✅ Report generated successfully")
            print(f"   - Total repos: {len(repos)}")
            print(f"   - Timestamp: {data.get('generated_at')}")
            if no_profile:
                print(f"   - Observer repos: {len(no_profile)}")
            print("✅ CI validation passed (fleet state not checked in CI)")
            return 0

        # Full validation (local mode)
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
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON report: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
