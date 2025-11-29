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
  local exit_code=0
  local dryrun_mode="${DRYRUN:-0}"
  (
    cd "$tmpdir/$repo_name"
    git add .
    if git diff --staged --quiet; then
      log "  No changes to commit"
      exit 0
    fi
    
    if (( dryrun_mode == 1 )); then
      log "  [DRY-RUN] Would commit $copied files"
      git diff --staged --stat
      exit 0
    fi
    
    # Use configurable git user (with defaults)
    local git_email="${WGX_GIT_EMAIL:-wgx-bot@heimgewebe.local}"
    local git_name="${WGX_GIT_NAME:-WGX Bot}"
    git config user.email "$git_email"
    git config user.name "$git_name"
    
    # Fetch and check for existing branch
    git fetch origin "chore/wgx-template-sync" 2>/dev/null || true
    local branch_exists_remote=0
    if git rev-parse --verify "origin/chore/wgx-template-sync" >/dev/null 2>&1; then
      branch_exists_remote=1
    fi
    
    local branch_exists_local=0
    if git rev-parse --verify "chore/wgx-template-sync" >/dev/null 2>&1; then
      branch_exists_local=1
    fi
    
    # Handle branch checkout/creation
    if (( branch_exists_local == 1 )); then
      # Local branch exists, just switch to it
      if ! git checkout "chore/wgx-template-sync" 2>/dev/null; then
        log "  Failed to checkout existing local branch chore/wgx-template-sync"
        exit 1
      fi
    elif (( branch_exists_remote == 1 )); then
      # Remote exists but local doesn't, create local tracking branch
      if ! git checkout -b "chore/wgx-template-sync" "origin/chore/wgx-template-sync" 2>/dev/null; then
        log "  Failed to create local branch from remote chore/wgx-template-sync"
        exit 1
      fi
    else
      # Neither exists, create new branch
      if ! git checkout -b "chore/wgx-template-sync"; then
        log "  Failed to create new branch chore/wgx-template-sync"
        exit 1
      fi
    fi
    
    git commit -m "chore(templates): sync from metarepo via wgx"
    
    if command -v gh >/dev/null 2>&1; then
      local push_output
      if ! push_output=$(git push -u origin "chore/wgx-template-sync" 2>&1); then
        log "  Push failed - may need manual intervention"
        log "  Error: $push_output"
        exit 1
      fi
      gh pr create --title "chore(templates): sync from metarepo" \
        --body "Automated template sync via wgx up" \
        --base "$default_branch" \
        --head "chore/wgx-template-sync" 2>/dev/null || log "  PR may already exist"
    else
      log "  gh CLI not found - skipping PR creation. Branch: chore/wgx-template-sync"
    fi
    
    log "  ✓ Synced $copied files"
    exit 0
  ) || exit_code=$?
  
  return $exit_code
}
