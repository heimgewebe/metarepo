#!/bin/bash
# scripts/tools/lychee-install.sh
#
# Helper script to download the latest lychee release executable into /usr/local/bin.
# Used by CI workflows to ensure lychee is available without pinning to a specific version.

set -euo pipefail

# If lychee is already installed, exit early.
if command -v lychee >/dev/null 2>&1; then
	echo "lychee is already installed at $(command -v lychee)"
	exit 0
fi

echo "Fetching latest lychee release tag from GitHub API"
LATEST_TAG=$(curl -sSf "https://api.github.com/repos/lycheeverse/lychee/releases/latest" | jq -r '.tag_name')

if [[ -z "$LATEST_TAG" ]]; then
	echo "Could not determine latest lychee release tag. Exiting."
	exit 1
fi

ARCHIVE="lychee-${LATEST_TAG}-x86_64-unknown-linux-gnu.tar.gz"
URL="https://github.com/lycheeverse/lychee/releases/download/${LATEST_TAG}/${ARCHIVE}"

echo "Downloading lychee from ${URL}"
TMP_DIR=$(mktemp -d)
trap 'rm -rf -- "$TMP_DIR"' EXIT

curl -sSfL --retry 3 --retry-delay 2 "${URL}" -o "${TMP_DIR}/lychee.tar.gz"

echo "Extracting archive..."
tar -xzf "${TMP_DIR}/lychee.tar.gz" -C "${TMP_DIR}"

echo "Installing lychee binary to /usr/local/bin/"
sudo mv "${TMP_DIR}/lychee" /usr/local/bin/lychee

echo "Installation complete. Verifying lychee version:"
lychee --version
