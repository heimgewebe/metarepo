#!/usr/bin/env bash
set -euo pipefail

# Setup: Store original toolchain and create a temporary one for tests
# This ensures our tests are hermetic and don't depend on the real file.
ORIG_TOOLCHAIN=""
if [ -f "toolchain.versions.yml" ]; then
	ORIG_TOOLCHAIN=$(cat "toolchain.versions.yml")
fi
# Cleanup executes on exit, restoring the original toolchain file
cleanup() {
	local exit_code=$?
	if [ -n "${ORIG_TOOLCHAIN}" ]; then
		echo "${ORIG_TOOLCHAIN}" >toolchain.versions.yml
	else
		rm -f toolchain.versions.yml
	fi
	exit $exit_code
}
trap cleanup EXIT

# Test runner function
assert_url() {
	local description="$1"
	local just_version_override="$2"
	local libc_override="$3"
	local expected_url="$4"

	local cmd_env=(DRY_RUN=1)
	[ -n "${just_version_override}" ] && cmd_env+=("JUST_VERSION=${just_version_override}")
	[ -n "${libc_override}" ] && cmd_env+=("JUST_LIBC=${libc_override}")

	# The script to test
	local script_to_run="scripts/tools/just-pin.sh"

	# Execute the script with the specified environment
	local out
	out=$(env "${cmd_env[@]}" bash "${script_to_run}")

	# Assertion
	if [[ "$out" != "${expected_url}" ]]; then
		echo "FAIL: ${description}"
		echo "  Expected: ${expected_url}"
		echo "  Got:      ${out}"
		exit 1
	else
		echo "PASS: ${description}"
	fi
}

ARCH=$(uname -m)
if [[ "$ARCH" == "amd64" ]]; then
	ARCH="x86_64"
elif [[ "$ARCH" == "arm64" ]]; then
	ARCH="aarch64"
fi
YQ_VERSION_FOR_TEST="v4.44.3"

# --- Test Cases ---

# 1) Legacy tests: Assert correct URL on Linux/glibc with JUST_VERSION override
assert_url \
	"Legacy: Linux/glibc URL (JUST_VERSION override)" \
	"1.14.0" \
	"gnu" \
	"https://github.com/casey/just/releases/download/1.14.0/just-1.14.0-${ARCH}-unknown-linux-gnu.tar.gz"

# 2) Legacy tests: Assert musl mapping with JUST_VERSION override
assert_url \
	"Legacy: Linux/musl URL (JUST_VERSION override)" \
	"1.14.0" \
	"musl" \
	"https://github.com/casey/just/releases/download/1.14.0/just-1.14.0-${ARCH}-unknown-linux-musl.tar.gz"

# 3) New test: Read version from our temporary toolchain.versions.yml
# This version has a 'v' prefix, which is important to test.
echo "just: 'v1.25.0'" >toolchain.versions.yml
echo "yq: '${YQ_VERSION_FOR_TEST}'" >>toolchain.versions.yml
assert_url \
	"New: Reads from toolchain.yml (v-prefix)" \
	"" \
	"gnu" \
	"https://github.com/casey/just/releases/download/v1.25.0/just-1.25.0-${ARCH}-unknown-linux-gnu.tar.gz"

# 4) New test: Read a version without 'v' prefix from toolchain
echo "just: '1.26.0'" >toolchain.versions.yml
echo "yq: '${YQ_VERSION_FOR_TEST}'" >>toolchain.versions.yml
assert_url \
	"New: Reads from toolchain.yml (no v-prefix)" \
	"" \
	"musl" \
	"https://github.com/casey/just/releases/download/1.26.0/just-1.26.0-${ARCH}-unknown-linux-musl.tar.gz"

# 5) New test: JUST_VERSION override should still take precedence over the toolchain file
echo "just: 'v1.25.0'" >toolchain.versions.yml
echo "yq: '${YQ_VERSION_FOR_TEST}'" >>toolchain.versions.yml
assert_url \
	"New: JUST_VERSION overrides toolchain.yml" \
	"1.30.0" \
	"gnu" \
	"https://github.com/casey/just/releases/download/1.30.0/just-1.30.0-${ARCH}-unknown-linux-gnu.tar.gz"

echo "All offline tests passed."
