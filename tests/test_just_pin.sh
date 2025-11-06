#!/usr/bin/env bash
set -euo pipefail

ARCH=$(uname -m)
if [[ "$ARCH" == "amd64" ]]; then
  ARCH="x86_64"
elif [[ "$ARCH" == "arm64" ]]; then
  ARCH="aarch64"
fi

# 1) Assert correct URL on Linux/glibc
out="$(JUST_VERSION=1.14.0 JUST_LIBC=gnu DRY_RUN=1 bash scripts/tools/just-pin.sh)"
if [[ "$out" != "https://github.com/casey/just/releases/download/1.14.0/just-1.14.0-${ARCH}-unknown-linux-gnu.tar.gz" ]]; then
  echo "Assertion failed for glibc"
  exit 1
fi

# 2) Assert musl mapping
out2="$(JUST_VERSION=1.14.0 JUST_LIBC=musl DRY_RUN=1 bash scripts/tools/just-pin.sh)"
if [[ "$out2" != "https://github.com/casey/just/releases/download/1.14.0/just-1.14.0-${ARCH}-unknown-linux-musl.tar.gz" ]]; then
  echo "Assertion failed for musl"
  exit 1
fi

echo "Offline tests passed"
