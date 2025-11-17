#!/usr/bin/env bash
set -euo pipefail
# render-diagram.sh — rendert Mermaid-Diagramme (mmd oder Markdown-Codeblöcke) nach PNG/SVG.
# Voraussetzungen (CI installiert automatisch):
#   - node + npx (für @mermaid-js/mermaid-cli)
#
# Nutzung:
#   scripts/render-diagram.sh docs/IDEal_Blueprint.md docs/heimgewebe-architektur.mmd \
#                               --outdir docs/diagrams --format png
#
# Hinweise:
#   - .mmd Dateien werden direkt gerendert
#   - In .md werden die ersten ```mermaid```-Blöcke extrahiert und einzeln gerendert:
#       <dateiname>__blk<nr>.<png|svg>

OUTDIR="docs/diagrams"
FORMAT="png"
THEME="default" # "dark","forest","neutral" etc. (mmdc --help)

ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --outdir) OUTDIR="$2"; shift 2;;
    --format) FORMAT="$2"; shift 2;;
    --theme)  THEME="$2";  shift 2;;
    *) ARGS+=("$1"); shift;;
  esac
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Usage: $0 <files...> [--outdir docs/diagrams] [--format png|svg] [--theme default]" >&2
  exit 1
fi

mkdir -p "$OUTDIR"

have_npx() { command -v npx >/dev/null 2>&1; }
have_npx || { echo "npx nicht gefunden (Node). Bitte Node/npm installieren." >&2; exit 1; }

# Warmup ajv-cli einmal (download cache)
npx --yes @mermaid-js/mermaid-cli@10.9.1 --version >/dev/null

render_mmd() {
  local in="$1" out_base="$2"
  local out="${OUTDIR}/${out_base}.${FORMAT}"
  # Preprocess to remove markdown fences, write to temp file
  local tmp_mmd
  tmp_mmd="$(mktemp)"
  trap 'rm -f "$tmp_mmd"' RETURN
  sed '/^```/d' "$in" > "$tmp_mmd"

  echo "→ render ${in}  ->  ${out}"
  npx --yes @mermaid-js/mermaid-cli@10.9.1 \
      --puppeteerConfigFile "puppeteer-config.json" \
      -i "$tmp_mmd" -o "$out" -t "$THEME" -s 1 >/dev/null
}

extract_md_mermaid_blocks() {
  # Druckt blockweise Mermaid-Inhalte mit Nullbyte-Trennzeichen
  # und Zeilen "===BLOCK:<n>:<safe_base>===" als Header je Block auf stderr
  local file="$1"
  local base="$(basename "${file%.*}")"
  awk -v base="$base" '
    BEGIN {in=0; n=0}
    /^```[ \t]*mermaid[ \t]*$/ {in=1; n++; next}
    /^```[ \t]*$/ && in==1 {in=0; printf("\n"); next}
    { if(in==1) printf("%s\n",$0); else if(in==0 && n>0 && $0=="") {} }
  ' "$file"
}

for f in "${ARGS[@]}"; do
  [[ -f "$f" ]] || { echo "Datei nicht gefunden: $f" >&2; continue; }
  ext="${f##*.}"
  base="$(basename "$f")"
  stem="${base%.*}"
  if [[ "$ext" == "mmd" ]]; then
    render_mmd "$f" "$stem"
  elif [[ "$ext" == "md" ]]; then
    # Extrahiere mermaid-Blöcke in temp Dateien und rendere nummeriert
    tmpdir="$(mktemp -d)"; trap 'rm -rf "$tmpdir"' EXIT
    mapfile -t blocks < <(grep -n '```[[:space:]]*mermaid' -n "$f" | cut -d: -f1)
    if (( ${#blocks[@]} == 0 )); then
      echo "Hinweis: keine \`\`\`mermaid Codeblöcke in $f gefunden – übersprungen."
      continue
    fi
    # robustes Extrahieren
    count=0
    in=0
    outfile=""
    while IFS= read -r line; do
      if [[ "$line" =~ ^\`\`\`[[:space:]]*mermaid[[:space:]]*$ ]]; then
        ((count++))
        outfile="${tmpdir}/${stem}__blk${count}.mmd"
        in=1
        continue
      fi
      if [[ "$line" =~ ^\`\`\`[[:space:]]*$ ]] && [[ $in -eq 1 ]]; then
        in=0
        continue
      fi
      if [[ $in -eq 1 ]]; then
        printf '%s\n' "$line" >> "$outfile"
      fi
    done < "$f"
    if (( count == 0 )); then
      echo "Hinweis: keine mermaid-Blöcke extrahiert in $f – übersprungen."
      continue
    fi
    for b in "$tmpdir"/*.mmd; do
      blk="$(basename "$b" .mmd)"
      render_mmd "$b" "$blk"
    done
  else
    echo "Unbekannter Typ ($ext) – nur .mmd oder .md werden unterstützt: $f" >&2
  fi
done

echo "✓ Rendering abgeschlossen -> $OUTDIR"
