#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob

fail=0

# ----------------------------------------
# 1. Check: Filenamen, Header & Metadaten
# ----------------------------------------

for f in docs/adrs/[0-9]*-*.md; do
  bn="$(basename "$f")"
  num="${bn%%-*}"

  # H1-Header prüfen: "# ADR-<NUM> <Title>"
  header="$(head -n 1 "$f" || echo "")"
  if [[ $header =~ ^\#\ ADR-([0-9]+)\  ]]; then
    hnum="${BASH_REMATCH[1]}"
    if [[ "$hnum" != "$num" ]]; then
      echo "::error file=$bn::ADR number mismatch between filename ('$num') and header ('$hnum')"
      fail=1
    fi
  else
    echo "::error file=$bn::Missing or invalid H1 ADR header (expected '# ADR-${num} <Title>')"
    fail=1
  fi

  # Datum prüfen (Pflicht, Format + parsebar)
  datum="$(grep -m1 '^Datum:' "$f" | awk '{print $2}' || true)"
  if [[ -z "${datum:-}" ]]; then
    echo "::error file=$bn::Missing 'Datum: YYYY-MM-DD' line"
    fail=1
  elif ! [[ "$datum" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "::error file=$bn::Invalid Datum '$datum' (expected YYYY-MM-DD)"
    fail=1
  elif ! date -d "$datum" +%s >/dev/null 2>&1; then
    echo "::error file=$bn::Unable to parse Datum '$datum'"
    fail=1
  fi

  # Status prüfen (Governance: Proposed → Accepted → Superseded; andere Werte = Warning)
  status_raw="$(grep -m1 '^Status:' "$f" | awk '{print $2}' || true)"
  status="$(printf '%s' "${status_raw:-}" | tr 'A-Z' 'a-z')"

  if [[ -z "${status:-}" ]]; then
    echo "::error file=$bn::Missing 'Status:' line"
    fail=1
  elif [[ "$status" != "proposed" && "$status" != "accepted" && "$status" != "superseded" ]]; then
    echo "::warning file=$bn::Unexpected Status '$status_raw' (expected: Proposed|Accepted|Superseded)"
  fi
done

# ----------------------------------------
# 2. Check: Stale Proposed ADRs (> 7 Tage)
# ----------------------------------------

now_ts="$(date +%s)"

for f in docs/adrs/[0-9]*-*.md; do
  bn="$(basename "$f")"

  # Template nicht bewerten
  if [[ "$bn" == "000-template.md" ]]; then
    continue
  fi

  status_raw="$(grep -m1 '^Status:' "$f" | awk '{print $2}' || true)"
  status="$(printf '%s' "${status_raw:-}" | tr 'A-Z' 'a-z')"
  date_str="$(grep -m1 '^Datum:' "$f" | awk '{print $2}' || true)"

  if [[ "$status" == "proposed" ]]; then
    if ! [[ "$date_str" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      echo "::error file=$bn::Invalid or missing Datum '$date_str' (expected YYYY-MM-DD)"
      fail=1
      continue
    fi

    if ! build_ts="$(date -d "$date_str" +%s 2>/dev/null)"; then
      echo "::error file=$bn::Unable to parse Datum '$date_str'"
      fail=1
      continue
    fi

    days=$(( ( now_ts - build_ts ) / 86400 ))
    if (( days > 7 )); then
      echo "::warning file=$bn::ADR is still 'Proposed' after $days days – please review, accept, reject or update it"
    fi
  fi
done

exit "$fail"
