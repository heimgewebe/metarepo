#!/usr/bin/env bash
#
# heimgewebe MCP – lokales Setup für den MCP-Server "heimgewebe-local"
#
# Dieses Skript:
#   1. findet das Repo-Root
#   2. prüft servers/local-mcp
#   3. installiert Abhängigkeiten (@modelcontextprotocol/sdk)
#   4. prüft, ob Node und das SDK nutzbar sind
#

set -euo pipefail

echo "== heimgewebe MCP local setup =="

if ! command -v git >/dev/null 2>&1; then
  echo "error: git not found; run this inside a git repository clone." >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SERVER_DIR="${ROOT}/servers/local-mcp"

echo "-> Repo root: ${ROOT}"
echo "-> MCP server dir: ${SERVER_DIR}"

if [ ! -d "${SERVER_DIR}" ]; then
  echo "error: ${SERVER_DIR} not found."
  echo "       Did you already add servers/local-mcp (MCP server) to this repo?" >&2
  exit 1
fi

cd "${SERVER_DIR}"

if [ ! -f package.json ]; then
  echo "error: package.json missing in ${SERVER_DIR}." >&2
  echo "       Expected @modelcontextprotocol/sdk here." >&2
  exit 1
fi

PKG_MANAGER=""

if command -v pnpm >/dev/null 2>&1; then
  PKG_MANAGER="pnpm"
elif command -v npm >/dev/null 2>&1; then
  PKG_MANAGER="npm"
fi

if [ -z "${PKG_MANAGER}" ]; then
  echo "error: neither pnpm nor npm found in PATH." >&2
  echo "       Please install pnpm or npm before running this script." >&2
  exit 1
fi

echo "-> Using package manager: ${PKG_MANAGER}"

if [ "${PKG_MANAGER}" = "pnpm" ]; then
  pnpm install
else
  npm install
fi

NODE_BIN="${NODE_BIN:-node}"

if ! command -v "${NODE_BIN}" >/dev/null 2>&1; then
  echo "error: node not found." >&2
  echo "       Please install Node.js (empfohlen: v20 oder neuer) or set NODE_BIN." >&2
  exit 1
fi

echo "-> Verifying MCP SDK usability..."
# Check for specific entry point because root export might be missing in some versions
if ! "${NODE_BIN}" --input-type=module -e "import '@modelcontextprotocol/sdk/server/mcp.js';" >/dev/null 2>&1; then
  echo "error: unable to load '@modelcontextprotocol/sdk/server/mcp.js'." >&2
  echo "       Check node version and node_modules in ${SERVER_DIR}." >&2
  exit 1
fi

echo
echo "OK: heimgewebe-local MCP server dependencies installed and basic check passed."
echo
echo "Next steps:"
echo "  1. Ensure that .mcp/registry.json exists in the repo root and"
echo "     has an entry for the 'heimgewebe-local' server, e.g.:"
echo '       { "type": "process", "command": "node", "args": ["servers/local-mcp/index.js"], ... }'
echo "  2. In your IDE (z.B. VS Code mit Copilot Agent Mode), point the MCP configuration"
echo "     to this registry file."
echo "  3. Use Copilot Chat / Agent Mode and call tools like 'wgx_guard' or 'wgx_smoke'."
echo
echo "Hint:"
echo "  If something fails, re-run this script with 'bash -x tools/mcp-local-setup.sh'"
echo "  to see each step in detail."
echo

exit 0
