#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <expected-head>" >&2
  exit 2
fi

EXPECTED_HEAD="$1"
REPO_ROOT="$(git rev-parse --show-toplevel)"
HEAD="$(git -C "${REPO_ROOT}" rev-parse HEAD)"

if [[ "${HEAD}" != "${EXPECTED_HEAD}" ]]; then
  echo "HEAD mismatch: expected ${EXPECTED_HEAD}, observed ${HEAD}" >&2
  exit 2
fi
if ! git -C "${REPO_ROOT}" diff --quiet HEAD -- || ! git -C "${REPO_ROOT}" diff --cached --quiet; then
  echo "tracked repository state is dirty" >&2
  exit 2
fi

BASE="${HOME}/.local/share/renovate-fleet"
RELEASE="${BASE}/releases/${HEAD}"
CURRENT="${BASE}/current"
UNIT_DIR="${HOME}/.config/systemd/user"
TMP="${BASE}/.release-${HEAD}-$$"

mkdir -p "${BASE}/releases" "${UNIT_DIR}"
rm -rf "${TMP}"
mkdir -p "${TMP}"
git -C "${REPO_ROOT}" archive "${HEAD}" automation/renovate | tar -x -C "${TMP}"

if [[ ! -e "${RELEASE}" ]]; then
  mv "${TMP}" "${RELEASE}"
else
  rm -rf "${TMP}"
fi

ln -sfn "${RELEASE}" "${BASE}/.current-${HEAD}"
mv -Tf "${BASE}/.current-${HEAD}" "${CURRENT}"

install -m 0644 "${RELEASE}/automation/renovate/systemd/renovate-fleet.service" "${UNIT_DIR}/renovate-fleet.service"
install -m 0644 "${RELEASE}/automation/renovate/systemd/renovate-fleet.timer" "${UNIT_DIR}/renovate-fleet.timer"
systemctl --user daemon-reload

printf '{"status":"installed","head":"%s","release":"%s","current":"%s"}\n' "${HEAD}" "${RELEASE}" "${CURRENT}"
