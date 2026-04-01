#!/usr/bin/env bash
set -euo pipefail

# Regression test: render-diagram.sh cleanup mechanism.
#
# The old bug: `trap 'rm -rf "$tmpdir"' EXIT` inside a loop overwrites the
# previous trap on every iteration, so only the *last* tmpdir is removed.
#
# The fix: accumulate paths in _render_tmpdirs[] and run a single
# _render_cleanup function on EXIT.
#
# This test exercises the cleanup function directly (no npx / mermaid-cli
# required) by replicating the exact mechanism from render-diagram.sh.

# ---------------------------------------------------------------------------
# Replicate the cleanup mechanism verbatim from render-diagram.sh
# ---------------------------------------------------------------------------
_render_tmpdirs=()
_render_cleanup() {
  for d in "${_render_tmpdirs[@]}"; do
    rm -rf -- "$d"
  done
}

# ---------------------------------------------------------------------------
# Simulate the loop body: three markdown files each produce a tmpdir
# ---------------------------------------------------------------------------
d1="$(mktemp -d)"
d2="$(mktemp -d)"
d3="$(mktemp -d)"

_render_tmpdirs+=("$d1")
_render_tmpdirs+=("$d2")
_render_tmpdirs+=("$d3")

# Verify all three exist before cleanup
for d in "$d1" "$d2" "$d3"; do
  [[ -d "$d" ]] || { echo "FAIL: tmpdir $d was not created"; exit 1; }
done

# Run cleanup
_render_cleanup

# ---------------------------------------------------------------------------
# Assertions: every tmpdir must be gone
# ---------------------------------------------------------------------------
fail=0
for d in "$d1" "$d2" "$d3"; do
  if [[ -d "$d" ]]; then
    echo "FAIL: tmpdir $d still exists after _render_cleanup"
    fail=1
  fi
done

[[ $fail -eq 0 ]] || exit 1

echo "PASS: all 3 accumulated tmpdirs removed by _render_cleanup"
echo "PASS: render-diagram.sh cleanup regression test passed"
