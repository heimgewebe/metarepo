#!/bin/bash
# scripts/tools/lychee-install.sh
#
# Helper script to download the latest lychee release executable into /usr/local/bin.
# Used by CI workflows to ensure lychee is available without pinning to a specific version.

set -euo pipefail

# If lychee is already installed, exit early.
if command -v lychee > /dev/null 2>&1; then
  echo "lychee is already installed at $(command -v lychee)"
  exit 0
fi

# Use GITHUB_TOKEN if available to avoid rate limits
: "${GITHUB_TOKEN:=}"
AUTH_HEADER=""
if [[ -n "${GITHUB_TOKEN}" ]]; then
  AUTH_HEADER="Authorization: token ${GITHUB_TOKEN}"
fi

echo "Fetching latest lychee release from GitHub API"
if [[ -n "${AUTH_HEADER}" ]]; then
  RELEASE_INFO=$(curl -sSf -H "${AUTH_HEADER}" "https://api.github.com/repos/lycheeverse/lychee/releases/latest")
else
  RELEASE_INFO=$(curl -sSf "https://api.github.com/repos/lycheeverse/lychee/releases/latest")
fi
URL=$(echo "$RELEASE_INFO" | jq -r '.assets[] | select(.name | endswith("x86_64-unknown-linux-gnu.tar.gz")) | .browser_download_url')

if [[ -z "$URL" ]]; then
  echo "Could not determine latest lychee release URL. Exiting."
  exit 1
fi

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
