#!/usr/bin/env bash
set -euo pipefail
# Minimaler Agent-Graph-Orchestrator (sequential/parallel stub)
# Läuft lokal, traced JSONL nach .agents/runs/<id>.jsonl
#
# Usage:
#   scripts/agents/orchestrate.sh agents/sample.workflow.json
#
# Requires: jq, timeout, date

WF="${1:-}"
[[ -f "$WF" ]] || { echo "usage: $0 <path/to/*.workflow.json>" >&2; exit 2; }

if ! command -v jq >/dev/null 2>&1; then
  echo "jq fehlt – installiere es (apt/brew) oder füge es in die CI-Toolchain ein." >&2
  exit 1
fi

readjson() { jq -r "${1}" "$WF"; }

workflow_id="$(readjson '.workflow_id')"
[[ -n "$workflow_id" && "$workflow_id" != "null" ]] || { echo "workflow_id fehlt" >&2; exit 1; }
orchestration="$(readjson '.orchestration // "sequential"')"
timeout_sec="$(readjson '.policies.timeout_sec // 0')"
retries="$(readjson '.policies.retry_strategy.max_retries // 0')"
backoff="$(readjson '.policies.retry_strategy.backoff // "none"')"

run_id="$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
outdir=".agents/runs"; mkdir -p "$outdir"
trace="${outdir}/${run_id}.jsonl"

ts(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log_event(){ # type payload_json
  local type="$1"; shift
  printf '{"ts":"%s","run":"%s","workflow":"%s","type":"%s","payload":%s}\n' \
    "$(ts)" "$run_id" "$workflow_id" "$type" "${1:-{}}" | tee -a "$trace" >/dev/null
}

log_event start '{}'
log_event meta "$(jq -n --arg wf "$WF" --arg orch "$orchestration" \
  --argjson timeout "$timeout_sec" --argjson retries "$retries" --arg back "$backoff" \
  '{workflow_file:$wf, orchestration:$orch, timeout_sec:$timeout, retries:$retries, backoff:$back}')"

# read agents into indexable arrays
agents_len="$(jq '.agents|length' "$WF")"
(( agents_len > 0 )) || { echo "agents[] leer" >&2; exit 1; }

run_one(){
  local idx="$1"
  local agent_json
  agent_json="$(jq ".agents[$idx]" "$WF")"
  local id type; id="$(jq -r '.id' <<<"$agent_json")"; type="$(jq -r '.type' <<<"$agent_json")"
  local cmd env_json; cmd="$(jq -rc '.command? // empty' <<<"$agent_json")"
  env_json="$(jq -rc '.env? // {}' <<<"$agent_json")"
  [[ "$id" != "null" && -n "$id" ]] || id="agent-$idx"

  log_event agent_start "$(jq -n --arg id "$id" --arg type "$type" '{id:$id,type:$type}')"

  # build environment
  mapfile -t env_kv < <(jq -r 'to_entries[] | "\(.key)=\(.value)"' <<<"$env_json" 2>/dev/null || true)
  # command can be string or array
  declare -a CMD
  if [[ -n "$cmd" ]]; then
    if [[ "$cmd" == \"*\" ]]; then
      # string
      CMD=(bash -lc "$(jq -r '.' <<<"$cmd")")
    else
      # array
      mapfile -t CMD < <(jq -r '.[]' <<<"$cmd")
    fi
  else
    # default: no-op
    CMD=(echo "no-op for" "$id")
  fi

  local try=0 rc=1 started elapsed_s
  while :; do
    try=$((try+1))
    started=$(date +%s)
    log_event exec_try "$(jq -n --arg id "$id" --argjson try "$try" --argjson timeout "$timeout_sec" '{id:$id,try:$try,timeout_sec:$timeout}')"
    if (( timeout_sec > 0 )); then
      (export "${env_kv[@]}" || true; timeout -- "${timeout_sec}s" "${CMD[@]}") 2> >(sed 's/^/stderr: /' >&2)
      rc=$?
    else
      (export "${env_kv[@]}" || true; "${CMD[@]}") 2> >(sed 's/^/stderr: /' >&2)
      rc=$?
    fi
    elapsed_s=$(( $(date +%s) - started ))
    log_event exec_done "$(jq -n --arg id "$id" --argjson rc "$rc" --argjson secs "$elapsed_s" '{id:$id,rc:$rc,secs:$secs}')"
    if (( rc == 0 )); then break; fi
    if (( try > retries )); then break; fi
    case "$backoff" in
      none) sleep 0;;
      fixed) sleep 2;;
      exponential) sleep $(( 2**(try-1) ));;
      *) sleep 1;;
    esac
  done
  if (( rc != 0 )); then
    log_event agent_fail "$(jq -n --arg id "$id" --argjson rc "$rc" '{id:$id,rc:$rc}')"
  else
    log_event agent_ok "$(jq -n --arg id "$id" '{id:$id}')"
  fi
  return "$rc"
}

rc=0
case "$orchestration" in
  sequential)
    for i in $(seq 0 $((agents_len-1))); do
      if ! run_one "$i"; then rc=1; break; fi
    done
    ;;
  parallel)
    # naive parallel: fire-and-wait; stop on first failure
    pids=()
    for i in $(seq 0 $((agents_len-1))); do
      ( run_one "$i" ) & pids+=("$!")
    done
    for p in "${pids[@]}"; do
      if ! wait "$p"; then rc=1; fi
    done
    ;;
  *)
    echo "orchestration '$orchestration' noch nicht unterstützt (verwende 'sequential' oder 'parallel')." >&2
    rc=2
    ;;
esac

if (( rc == 0 )); then
  log_event done "{}"
else
  log_event error "$(jq -n --arg reason "workflow_failed" '{reason:$reason}')"
fi
echo "::notice ::trace written to ${trace}"
exit "$rc"
