#!/usr/bin/env bash
set -euo pipefail

# Regression test: decision-preimage.bash must build the remote ref as
# refs/remotes/origin/<base>, not refs/remotes/<base>.
#
# Old (broken): base="refs/remotes/${GITHUB_BASE_REF}"   → refs/remotes/main
# New (correct): base="origin/${GITHUB_BASE_REF}"         → refs/remotes/origin/main
#                git show-ref ... "refs/remotes/${base}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GUARD="${REPO_ROOT}/wgx/guards/decision-preimage.bash"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Fake git: logs every invocation, returns suitable exit codes so the guard
# reaches the show-ref call without aborting.
# ---------------------------------------------------------------------------
GIT_CALL_LOG="${tmpdir}/git-calls.log"
export GIT_CALL_LOG
: > "${GIT_CALL_LOG}"

cat > "${tmpdir}/git" << 'GITEOF'
#!/usr/bin/env bash
echo "$*" >> "$GIT_CALL_LOG"
case "$1" in
  rev-parse)  exit 0 ;;          # --is-inside-work-tree → inside repo
  show-ref)   exit 1 ;;          # ref not found → guard takes fallback path
  diff)       exit 0 ;;          # no changed files
  *)          exit 0 ;;
esac
GITEOF
chmod +x "${tmpdir}/git"

# Fake jq: needed so the guard does not exit early on "jq not found".
cat > "${tmpdir}/jq" << 'JQEOF'
#!/usr/bin/env bash
exit 0
JQEOF
chmod +x "${tmpdir}/jq"

# Run guard; it always exits 0 (warn-only), so failures come from assertions.
GITHUB_BASE_REF=main \
  PATH="${tmpdir}:${PATH}" \
  bash "${GUARD}" 2>/dev/null || true

# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------
fail=0

# 1) The correct ref must be present.
if grep -qF "show-ref --verify --quiet refs/remotes/origin/main" "${GIT_CALL_LOG}"; then
  echo "PASS: git show-ref called with correct ref 'refs/remotes/origin/main'"
else
  echo "FAIL: expected 'refs/remotes/origin/main' in git calls"
  echo "--- actual git calls ---"
  cat "${GIT_CALL_LOG}"
  fail=1
fi

# 2) The old broken form must NOT be present (refs/remotes/main without origin).
#    Use a word-boundary pattern: the line must end after 'main' – i.e. there is
#    no 'origin' segment between 'refs/remotes/' and 'main'.
if grep -qE "show-ref.*refs/remotes/main( |$)" "${GIT_CALL_LOG}" 2>/dev/null; then
  echo "FAIL: old broken ref 'refs/remotes/main' found – regression!"
  echo "--- actual git calls ---"
  cat "${GIT_CALL_LOG}"
  fail=1
else
  echo "PASS: broken ref 'refs/remotes/main' (without origin) is absent"
fi

[[ $fail -eq 0 ]] || exit 1
echo "All decision-preimage ref regression tests passed."
