#!/usr/bin/env bash
# Apply reconciliation patches to fleet repositories
set -euo pipefail

red() { printf "\e[31m%s\e[0m\n" "$*"; }
green() { printf "\e[32m%s\e[0m\n" "$*"; }
yellow() { printf "\e[33m%s\e[0m\n" "$*"; }

OWNER="${GITHUB_OWNER:-heimgewebe}"
PATCHES_DIR="reports/patches"
WORK_DIR="$(mktemp -d)"
BRANCH_NAME="chore/reconcile-from-metarepo"

cleanup() {
  if [[ -d "$WORK_DIR" ]]; then
    rm -rf "$WORK_DIR"
  fi
}
trap cleanup EXIT INT TERM

apply_patch_to_repo() {
  local repo_name="$1"
  local patch_file="$PATCHES_DIR/${repo_name}.patch"
  
  if [[ ! -f "$patch_file" ]]; then
    yellow "No patch file for $repo_name, skipping..."
    return 0
  fi
  
  # Check if patch has any content
  if [[ ! -s "$patch_file" ]]; then
    yellow "Empty patch file for $repo_name, skipping..."
    return 0
  fi
  
  green "=== Applying patch to $repo_name ==="
  
  local repo_url="https://github.com/${OWNER}/${repo_name}.git"
  local repo_dir="$WORK_DIR/$repo_name"
  
  # Clone the repository
  echo "Cloning $repo_url..."
  if ! git clone --depth=1 "$repo_url" "$repo_dir" 2>&1; then
    red "Failed to clone $repo_name"
    return 1
  fi
  
  cd "$repo_dir"
  
  # Store absolute path to patch before changing directories
  local abs_patch_file
  abs_patch_file="$(cd "$(dirname "$patch_file")" && pwd)/$(basename "$patch_file")"
  
  # Configure git
  git config user.email "codex-bot@heimgewebe.org"
  git config user.name "Codex Bot"
  
  # Create a new branch
  git checkout -b "$BRANCH_NAME" || {
    yellow "Branch $BRANCH_NAME might already exist, trying to switch..."
    git checkout "$BRANCH_NAME" || {
      red "Failed to create/checkout branch"
      return 1
    }
  }
  
  # Apply the patch
  echo "Applying patch from $abs_patch_file..."
  if git apply --check "$abs_patch_file" 2>&1; then
    git apply "$abs_patch_file"
    green "✓ Patch applied successfully"
  else
    red "✗ Patch check failed for $repo_name"
    echo "Attempting to apply with 3-way merge..."
    if git apply --3way "$abs_patch_file" 2>&1; then
      green "✓ Patch applied with 3-way merge"
    else
      red "✗ Failed to apply patch to $repo_name"
      return 1
    fi
  fi
  
  # Check if there are any changes
  if git diff --quiet && git diff --cached --quiet; then
    yellow "No changes after applying patch to $repo_name"
    return 0
  fi
  
  # Stage all changes
  git add -A
  
  # Commit changes with multiline message
  local commit_msg
  commit_msg="chore(fleet): reconcile templates and contracts from metarepo

Applied reconciliation patch from heimgewebe/metarepo.
This synchronizes:
- CI workflow templates
- Contract schemas
- WGX profiles
- Documentation structure

Source: metarepo/reports/patches/${repo_name}.patch"
  
  git commit -m "$commit_msg"
  
  green "✓ Changes committed to $BRANCH_NAME"
  
  # Push the branch
  echo "Pushing branch $BRANCH_NAME..."
  if git push -u origin "$BRANCH_NAME" 2>&1; then
    green "✓ Branch pushed successfully"
    echo ""
    echo "Next steps:"
    echo "  Create PR: https://github.com/${OWNER}/${repo_name}/compare/${BRANCH_NAME}?expand=1"
    echo ""
  else
    red "✗ Failed to push branch (might need authentication or permissions)"
    echo "You can manually push with:"
    echo "  cd $repo_dir && git push -u origin $BRANCH_NAME"
    return 1
  fi
  
  cd -
}

# Main execution
echo "Starting patch application to fleet repositories..."
echo "Owner: $OWNER"
echo "Patches directory: $PATCHES_DIR"
echo "Work directory: $WORK_DIR"
echo ""

# List all available patches
patches=($(find "$PATCHES_DIR" -name "*.patch" -exec basename {} .patch \;))

if [[ ${#patches[@]} -eq 0 ]]; then
  red "No patch files found in $PATCHES_DIR"
  exit 1
fi

green "Found ${#patches[@]} patch files:"
printf '  - %s\n' "${patches[@]}"
echo ""

# Apply patches to each repository
failed_repos=()
for repo in "${patches[@]}"; do
  if ! apply_patch_to_repo "$repo"; then
    failed_repos+=("$repo")
  fi
  echo ""
done

# Summary
echo "=========================================="
echo "Summary:"
echo "=========================================="
echo "Total patches: ${#patches[@]}"
echo "Successful: $((${#patches[@]} - ${#failed_repos[@]}))"
echo "Failed: ${#failed_repos[@]}"

if [[ ${#failed_repos[@]} -gt 0 ]]; then
  red "Failed repositories:"
  printf '  - %s\n' "${failed_repos[@]}"
  exit 1
else
  green "All patches applied successfully!"
fi
