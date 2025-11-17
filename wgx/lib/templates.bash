#!/usr/bin/env bash
set -euo pipefail

list_template_files(){
  [[ -d "$ROOT_DIR/templates" ]] || return 1
  ( cd "$ROOT_DIR/templates" && find . -type f -print | sed 's|^\./||' | LC_ALL=C sort )
}
