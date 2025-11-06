#!/usr/bin/env bash
set -euo pipefail

yq_required() {
	command -v yq >/dev/null 2>&1 || {
		echo "yq fehlt. Install: https://mikefarah.gitbook.io/yq/" >&2
		exit 1
	}
}
