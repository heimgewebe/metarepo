#!/bin/bash
set -e

# 1. Fix Contracts
echo "Fixing contracts..."

# Heimlern
echo "Fixing Heimlern contracts..."
rm -f external_repos/heimlern/contracts/aussen_event.schema.json
rm -f external_repos/heimlern/contracts/policy_feedback.schema.json
rm -f external_repos/heimlern/contracts/policy_snapshot.schema.json

cp contracts/aussen.event.schema.json external_repos/heimlern/contracts/
cp contracts/policy.decision.schema.json external_repos/heimlern/contracts/
cp contracts/policy.feedback.schema.json external_repos/heimlern/contracts/
cp contracts/policy.snapshot.schema.json external_repos/heimlern/contracts/

# Mitschreiber
echo "Fixing Mitschreiber contracts..."
cp contracts/os.context.text.embed.schema.json external_repos/mitschreiber/contracts/

# SemantAH
echo "Fixing SemantAH contracts..."
cp contracts/insights.schema.json external_repos/semantAH/contracts/

# 2. Fix Templates
echo "Fixing templates..."
for repo in external_repos/*; do
  repo_name=$(basename "$repo")
  if [ -d "$repo/.github/workflows" ]; then
    echo "Updating workflows in $repo_name..."
    # Copy all canonical workflows that exist in the target (update) or are core (add if missing? No, only update for now to avoid bloating)
    # Actually, I'll update strictly matching ones.
    for template in templates/.github/workflows/*.yml; do
      filename=$(basename "$template")
      if [ -f "$repo/.github/workflows/$filename" ]; then
        cp "$template" "$repo/.github/workflows/$filename"
      fi
    done

    # Force update pr-heimgewebe-commands.yml and wgx-guard.yml if they are missing?
    # Usually we want them everywhere. I'll stick to updating existing ones to be safe with patch generation.
  fi
done

# 3. Fix Profiles
echo "Fixing profiles..."

# WGX
if [ ! -f "external_repos/wgx/.wgx/profile.yml" ]; then
  mkdir -p external_repos/wgx/.wgx
  echo "class: tooling" > external_repos/wgx/.wgx/profile.yml
  echo "domain: platform" >> external_repos/wgx/.wgx/profile.yml
  echo "scope: metrics" >> external_repos/wgx/.wgx/profile.yml
fi

# Heimgeist
if [ ! -f "external_repos/heimgeist/.wgx/profile.yml" ]; then
  mkdir -p external_repos/heimgeist/.wgx
  echo "class: meta" > external_repos/heimgeist/.wgx/profile.yml
  echo "domain: observer" >> external_repos/heimgeist/.wgx/profile.yml
fi

# Plexer
if [ ! -f "external_repos/plexer/.wgx/profile.yml" ]; then
  mkdir -p external_repos/plexer/.wgx
  echo "class: service" > external_repos/plexer/.wgx/profile.yml
  echo "domain: routing" >> external_repos/plexer/.wgx/profile.yml
fi

# Contracts
if [ ! -f "external_repos/contracts/.wgx/profile.yml" ]; then
  mkdir -p external_repos/contracts/.wgx
  echo "class: library" > external_repos/contracts/.wgx/profile.yml
  echo "domain: contracts" >> external_repos/contracts/.wgx/profile.yml
fi

# 4. Generate Patches
echo "Generating patches..."
ROOT=$(pwd)
for repo in external_repos/*; do
  repo_name=$(basename "$repo")
  echo "Generating patch for $repo_name..."
  cd "$repo"

  # Check if there are changes
  git add .
  if ! git diff --cached --quiet; then
    git diff --cached --binary > "$ROOT/reports/patches/$repo_name.patch"
    echo "Patch created: reports/patches/$repo_name.patch"
  else
    echo "No changes for $repo_name"
  fi

  # Reset changes to keep the clone clean-ish (optional, but good practice)
  # git reset --hard HEAD
  # Actually, keep them so I can inspect if needed.
  cd "$ROOT"
done

echo "Done."
