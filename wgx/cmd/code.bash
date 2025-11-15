#!/usr/bin/env bash

cmd_code(){
  local sub="${1:-}"; shift || true
  case "${sub}" in
    init)
      local lang="${1:-}"; [[ -n "$lang" ]] || die "wgx code init <rust|python|shell>"
      local src="${ROOT_DIR}/templates/dev/${lang}"
      [[ -d "$src" ]] || die "keine Templates für ${lang} gefunden: ${src}"
      rsync -a "${src}/" "./"
      log "Templates für ${lang} kopiert."
      ;;
    lint)
      log "Lint (stub) – bitte projektspezifische Linter einhängen."
      ;;
    test)
      log "Test (stub) – delegiere an just test / cargo test / pytest."
      ;;
    gen)
      local name="${1:-}"; [[ -n "$name" ]] || die "wgx code gen <template-name>"
      local src="${ROOT_DIR}/templates/dev/${name}"
      [[ -d "$src" || -f "$src" ]] || die "Template nicht gefunden: ${src}"
      rsync -a "${src}/" "./" 2>/dev/null || cp "${src}" "./"
      log "Template ${name} generiert."
      ;;
    *)
      die "unknown: wgx code ${sub}"
      ;;
  esac
}
