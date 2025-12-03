#!/usr/bin/env bash
set -euo pipefail

log() { printf "%s\n" "$*" >&2; }
die() {
  echo "ERR: $*" >&2
  exit 1
}
