#!/usr/bin/env bash

cmd_agent(){
  local sub="${1:-}"; shift || true
  case "$sub" in
    run)
      local wf="${1:-agents/sample.workflow.json}"
      # orchestrator suchen (in Ziel-Repo nach Templates-Sync unter scripts/agents/)
      local orch=""
      if [[ -x "scripts/agents/orchestrate.sh" ]]; then
        orch="scripts/agents/orchestrate.sh"
      elif [[ -x "templates/scripts/agents/orchestrate.sh" ]]; then
        orch="templates/scripts/agents/orchestrate.sh"
      else
        echo "Orchestrator nicht gefunden. Erwartet scripts/agents/orchestrate.sh (oder templates/… für lokalen Test)." >&2
        exit 2
      fi
      if [[ ! -f "$wf" ]]; then
        echo "Workflow-Datei nicht gefunden: $wf" >&2
        echo "Tipp: Nutze agents/sample.workflow.json oder gib einen Pfad an." >&2
        exit 2
      fi
      bash "$orch" "$wf"
      ;;
    trace)
      local runfile="${1:-}"
      # trace-helfer suchen
      local trc=""
      if [[ -x "scripts/agents/trace.sh" ]]; then
        trc="scripts/agents/trace.sh"
      elif [[ -x "templates/scripts/agents/trace.sh" ]]; then
        trc="templates/scripts/agents/trace.sh"
      fi
      if [[ -z "$trc" ]]; then
        echo "Trace-Skript nicht gefunden (scripts/agents/trace.sh)." >&2
        exit 2
      fi
      if [[ -z "$runfile" ]]; then
        runfile="$(ls -1t .agents/runs/*.jsonl 2>/dev/null | head -n1 || true)"
        [[ -n "$runfile" ]] || { echo "Kein Run gefunden unter .agents/runs/*.jsonl"; exit 2; }
      fi
      bash "$trc" "$runfile"
      ;;
    validate)
      local manifest="${1:-}"; [[ -n "$manifest" ]] || die "wgx agent validate <manifest.yaml>"
      # naive yaml->json (nur sehr einfacher Fall) – für echte Nutzung: yq
      if command -v yq >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
        tmp="$(mktemp)"; yq -o=json '.' "$manifest" >"$tmp"
        npx --yes ajv-cli@5 validate --spec=draft2020 -s "${ROOT_DIR}/contracts/agent.workflow.schema.json" -d "$tmp" || die "Manifest verletzt Contract"
        rm -f "$tmp"
        log "OK: Agent-Manifest valid."
      else
        log "Hinweis: yq/npx fehlen – nur Format-Anwesenheit geprüft."
        [[ -s "$manifest" ]] || die "Manifest leer"
      fi
      ;;
    ""|-h|--help|help)
      cat <<'HLP'
wgx agent run [agents/<workflow>.json]   # Workflow lokal orchestrieren (sequential/parallel)
wgx agent trace [path/to/run.jsonl]      # Kompakte Trace-Ansicht des letzten/angegebenen Runs
wgx agent validate <manifest.yaml>       # Manifest gegen Contract prüfen
HLP
      ;;
    *)
      echo "Unbekanntes Subkommando: agent $sub" >&2
      exit 2
      ;;
  esac
}
