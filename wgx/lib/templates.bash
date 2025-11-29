#!/usr/bin/env bash
set -euo pipefail

list_template_files(){
  [[ -d "$ROOT_DIR/templates" ]] || return 1
  ( cd "$ROOT_DIR/templates" && find . -type f -print | sed 's|^\./||' | LC_ALL=C sort )
}

copy_templates_into_repo(){
  local repo_name="$1"
  local ow; ow="$(owner)"
  local tmpdir; tmpdir="$(mktemp -d)"
  _tmp_dirs+=("$tmpdir")
  
  local repo_url="https://github.com/${ow}/${repo_name}.git"
  local default_branch; default_branch="$(default_branch_of "$repo_name" || echo "main")"
  
  # Clone repo
  if ! git -c advice.detachedHead=false clone --depth=1 --branch="$default_branch" "$repo_url" "$tmpdir/$repo_name" >/dev/null 2>&1; then
    log "⚠ Clone failed: $repo_url (branch: $default_branch)"
    return 1
  fi
  
  # Copy templates
  local -a template_files=()
  mapfile -t template_files < <(list_template_files)
  
  if [[ ${#template_files[@]} -eq 0 ]]; then
    log "  No template files to sync"
    return 0
  fi
  
  local copied=0
  for rel_path in "${template_files[@]}"; do
    [[ -z "$rel_path" ]] && continue
    local src="$ROOT_DIR/templates/$rel_path"
    local dst="$tmpdir/$repo_name/$rel_path"
    
    if [[ ! -f "$src" ]]; then
      continue
    fi
    
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
    (( copied++ ))
  done
  
  # Commit and push if changes exist
  (
    cd "$tmpdir/$repo_name"
    git add .
    if git diff --staged --quiet; then
      log "  No changes to commit"
      return 0
    fi
    
    if (( DRYRUN == 1 )); then
      log "  [DRY-RUN] Would commit $copied files"
      git diff --staged --stat
      return 0
    fi
    
    git config user.email "wgx-bot@heimgewebe.local"
    git config user.name "WGX Bot"
    git checkout -b "chore/wgx-template-sync" 2>/dev/null || git checkout "chore/wgx-template-sync"
    git commit -m "chore(templates): sync from metarepo via wgx"
    
    if command -v gh >/dev/null 2>&1; then
      git push -u origin "chore/wgx-template-sync" 2>&1 || {
        log "  Push failed - may need manual intervention"
        return 1
      }
      gh pr create --title "chore(templates): sync from metarepo" \
        --body "Automated template sync via wgx up" \
        --base "$default_branch" \
        --head "chore/wgx-template-sync" 2>/dev/null || log "  PR may already exist"
    else
      log "  gh CLI not found - skipping PR creation. Branch: chore/wgx-template-sync"
    fi
    
    log "  ✓ Synced $copied files"
  )
}
