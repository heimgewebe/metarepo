#!/usr/bin/env bash
set -euo pipefail

cmd_knowledge(){
  local sub="${1:-}"; shift || true
  case "${sub}" in
    extract)
      local out="knowledge.graph.json"
      cat >"$out" <<'JSON'
{"nodes":[{"id":"root","node_type":"concept","label":"root"}],"edges":[],"metadata":{"tags":["demo"]}}
JSON
      log "Knowledge Graph geschrieben: $out"
      ;;
    export)
      log "Export (stub) – formatiere für vault-kompatiblen Import."
      ;;
    validate)
      local file="${1:-knowledge.graph.json}"
      [[ -f "$file" ]] || die "Datei nicht gefunden: $file"
      if command -v npx >/dev/null 2>&1; then
        npx --yes ajv-cli@5 validate --spec=draft2020 -s "${ROOT_DIR}/contracts/knowledge.graph.schema.json" -d "$file" || die "Schema-Verstoß"
      else
        log "ajv-cli nicht vorhanden – skip."
      fi
      ;;
    *)
      die "unknown: wgx knowledge ${sub}"
      ;;
  esac
}
