#!/usr/bin/env bash
set -uo pipefail

# Test suite for scripts/lib/semver.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the semver library
# shellcheck source=scripts/lib/semver.sh
source "${ROOT_DIR}/scripts/lib/semver.sh"

# Test counters
tests_passed=0
tests_failed=0

test_case() {
  local have="$1"
  local want="$2"
  local expected="$3"
  local description="$4"
  local strict="${5:-0}"
  
  if semver_compare "$have" "$want" "$strict"; then
    result="OK"
  else
    result="FAIL"
  fi
  
  if [[ "$result" == "$expected" ]]; then
    echo "✅ PASS: $description"
    echo "   semver_compare('$have', '$want', strict=$strict) -> $result"
    ((tests_passed++)) || true
  else
    echo "❌ FAIL: $description"
    echo "   semver_compare('$have', '$want', strict=$strict) -> $result (expected: $expected)"
    ((tests_failed++)) || true
  fi
}

echo "Testing semver_compare function..."
echo ""

# Exact match tests
echo "=== Exact Match Tests ==="
test_case "4.49.2" "v4.49.2" "OK" "Exact match with v prefix"
test_case "v4.49.2" "4.49.2" "OK" "Exact match reverse v prefix"
test_case "4.49.2" "4.49.2" "OK" "Exact match no prefix"

# 1.x version tests (standard SemVer)
echo ""
echo "=== Standard SemVer Tests (major >= 1) ==="
test_case "4.49.3" "v4.49.2" "OK" "Newer patch version"
test_case "4.49.10" "v4.49.2" "OK" "Much newer patch version"
test_case "4.50.0" "v4.49.2" "OK" "Newer minor version"
test_case "4.50.1" "v4.49.2" "OK" "Newer minor and patch"
test_case "4.49.1" "v4.49.2" "FAIL" "Older patch version"
test_case "4.48.0" "v4.49.2" "FAIL" "Older minor version"
test_case "5.0.0" "v4.49.2" "FAIL" "Different major version (newer)"
test_case "3.99.99" "v4.49.2" "FAIL" "Different major version (older)"

# 0.x version tests (unstable API per SemVer spec)
echo ""
echo "=== 0.x Version Tests (unstable API) ==="
test_case "0.4.20" "0.4.20" "OK" "0.x exact match"
test_case "0.4.21" "0.4.20" "OK" "0.x newer patch (same minor)"
test_case "0.4.19" "0.4.20" "FAIL" "0.x older patch"
test_case "0.5.0" "0.4.20" "FAIL" "0.x different minor (breaking per SemVer)"
test_case "0.4.99" "0.4.20" "OK" "0.x much newer patch"
test_case "0.10.2" "0.10.2" "OK" "0.10.x exact match"
test_case "0.10.3" "0.10.2" "OK" "0.10.x newer patch"
test_case "0.11.0" "0.10.2" "FAIL" "0.10.x vs 0.11.x (breaking)"
test_case "0.9.0" "0.10.2" "FAIL" "0.10.x vs 0.9.x (older minor)"

# Strict mode tests
echo ""
echo "=== Strict Mode Tests ==="
test_case "4.49.2" "v4.49.2" "OK" "Strict: exact match" "1"
test_case "4.49.3" "v4.49.2" "FAIL" "Strict: newer patch rejected" "1"
test_case "4.50.0" "v4.49.2" "FAIL" "Strict: newer minor rejected" "1"
test_case "0.4.21" "0.4.20" "FAIL" "Strict: 0.x newer patch rejected" "1"

# Edge cases
echo ""
echo "=== Edge Cases ==="
test_case "1.0.0" "v1.0.0" "OK" "Minimum version 1.0.0"
test_case "1.0.1" "v1.0.0" "OK" "Patch upgrade from 1.0.0"
test_case "0.0.1" "0.0.1" "OK" "Very early 0.0.x version exact"
test_case "0.0.2" "0.0.1" "FAIL" "0.0.x minor must match (treated as breaking)"

echo ""
echo "======================================"
echo "Tests passed: $tests_passed"
echo "Tests failed: $tests_failed"
echo "======================================"

if [[ $tests_failed -eq 0 ]]; then
  echo "✅ All tests passed!"
  exit 0
else
  echo "❌ Some tests failed!"
  exit 1
fi
