#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TOOLCHAIN_FILE="toolchain.versions.yml"

DEFAULT_YQ="4.44.3"
DEFAULT_UV="0.7.0"
DEFAULT_RUST="stable"

read_yaml() {
	local path="$1"

	if [[ ! -f "$TOOLCHAIN_FILE" ]]; then
		printf ''
		return
	fi

	if command -v yq >/dev/null 2>&1; then
		yq -r "${path} // \"\"" "$TOOLCHAIN_FILE"
		return
	fi

	local key="${path#.}"
	local value
	value=$(sed -n "s/^${key}:[[:space:]]*\"\?\([^\"#]*\)\"\?.*$/\1/p" "$TOOLCHAIN_FILE" | head -n1 | tr -d '[:space:]')
	printf '%s\n' "$value"
}

YQ_VER="$(read_yaml '.yq' || true)"
UV_VER="$(read_yaml '.uv' || true)"
RUST_VER="$(read_yaml '.rust' || true)"

if [[ ! -f "$TOOLCHAIN_FILE" ]]; then
	echo "Warning: $TOOLCHAIN_FILE missing – falling back to defaults" >&2
fi

YQ_VER_TRIM="${YQ_VER#v}"
UV_VER_TRIM="${UV_VER#v}"
RUST_VER_EFF="${RUST_VER:-$DEFAULT_RUST}"

YQ_EFF="${YQ_VER_TRIM:-$DEFAULT_YQ}"
UV_EFF="${UV_VER_TRIM:-$DEFAULT_UV}"

YQ_DISPLAY="${YQ_VER:-$DEFAULT_YQ}"
UV_DISPLAY="${UV_VER:-$DEFAULT_UV}"

echo "Resolved: yq=${YQ_DISPLAY}  uv=${UV_DISPLAY}  rust=${RUST_VER_EFF}"

render() {
	local template="$1"
	local output="$2"
	sed -e "s/{{YQ_VERSION}}/${YQ_EFF}/g" \
		-e "s/{{UV_VERSION}}/${UV_EFF}/g" \
		-e "s/{{RUST_VERSION}}/${RUST_VER_EFF:-$DEFAULT_RUST}/g" \
		"$template" >"$output"
	echo "Wrote $output"
}

render ".devcontainer/_devcontainer-dind.template.json" ".devcontainer/devcontainer-dind.json"
render ".devcontainer/_devcontainer-socket.template.json" ".devcontainer/devcontainer-socket.json"

echo "Done."
