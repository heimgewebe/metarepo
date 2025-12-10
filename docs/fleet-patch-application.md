# Fleet Reconciliation Patch Application Guide

This document describes how to apply reconciliation patches from metarepo to fleet repositories.

## Overview

The `reports/patches/` directory contains reconciliation patches for fleet repositories. These patches synchronize templates, contracts, and configurations from the metarepo canonical source to individual fleet repositories.

### Patch Contents

Each `.patch` file contains the necessary changes to bring a specific repository in line with the metarepo templates:

- **CI workflow templates**: `.github/workflows/*.yml`
- **Contract schemas**: `contracts/*.schema.json`
- **WGX profiles**: `.wgx/profile.yml`
- **Documentation**: Various documentation updates

## Application Methods

### Method 1: Automated Application via GitHub Actions (Recommended)

Use the GitHub Actions workflow to automatically apply patches and create PRs:

1. Go to the **Actions** tab in the metarepo repository
2. Select the **Apply Fleet Patches** workflow
3. Click **Run workflow**
4. Configure options:
   - **repos**: Enter `all` to apply to all repos, or a comma-separated list (e.g., `heimlern,semantAH,wgx`)
   - **dry_run**: Enable to test without creating PRs

The workflow will:
- Clone each target repository
- Apply the corresponding patch
- Create a branch `chore/reconcile-from-metarepo`
- Open a Pull Request with the changes

### Method 2: Manual Application

For manual application of patches to individual repositories:

```bash
# Clone the target repository
git clone https://github.com/heimgewebe/<repo-name>.git
cd <repo-name>

# Create a branch
git checkout -b chore/reconcile-from-metarepo

# Apply the patch (from metarepo root)
git apply /path/to/metarepo/reports/patches/<repo-name>.patch

# Or use 3-way merge if there are conflicts
git apply --3way /path/to/metarepo/reports/patches/<repo-name>.patch

# Review changes
git diff

# Commit and push
git add -A
git commit -m "chore(fleet): reconcile templates and contracts from metarepo"
git push -u origin chore/reconcile-from-metarepo
```

Then create a PR on GitHub.

### Method 3: Using the Helper Script

You can also use the provided helper script (requires GitHub authentication):

```bash
cd /path/to/metarepo
./scripts/apply-fleet-patches.sh
```

**Note**: This script requires GitHub authentication with push access to all target repositories.

## Common Updates in Patches

Most patches include one or more of the following:

### 1. Workflow Standardization

- **`pr-heimgewebe-commands.yml`**: Updated to use `secrets: inherit` instead of explicit secret passing
- **`wgx-guard.yml`**: Delegates to canonical `heimgewebe/wgx/.github/workflows/wgx-guard.yml@main`
- **`wgx-smoke.yml`**: Delegates to canonical `heimgewebe/wgx/.github/workflows/wgx-smoke.yml@main`
- **`validate-knowledge-graph.yml`**: Enhanced validation with stricter checks and better error handling

### 2. Contract Schema Updates

- Renamed files to match canonical naming conventions (where applicable, e.g., in heimlern):
  - `aussen_event.schema.json` → `aussen.event.schema.json`
  - `policy_feedback.schema.json` → `policy.feedback.schema.json`
  - `policy_snapshot.schema.json` → `policy.snapshot.schema.json`
- Updated schema structures for consistency across the fleet
- Added `x-producers` and `x-consumers` metadata for better contract documentation

### 3. WGX Profile Additions

- Added missing `.wgx/profile.yml` for repos that didn't have them
- Standardized profile format with required fields (`class`, `domain`, `scope`)

## Repository-Specific Notes

### heimlern
- Contract schema updates (aussen.event, policy.decision, policy.feedback, policy.snapshot)
- Workflow updates for CI templates
- File renames to match canonical naming

### semantAH
- Updated `insights.schema.json` with new structure
- Workflow validation improvements
- Added `x-producers` and `x-consumers` metadata

### wgx
- Added `.wgx/profile.yml` (class: tooling, domain: platform)
- Simplified workflows to delegate to canonical source

### hausKI, weltgewebe, chronik, aussensensor, tools
- Standard CI template synchronization
- Workflow modernization to use `secrets: inherit`

### heimgeist, plexer, contracts
- Added missing `.wgx/profile.yml` configurations

### mitschreiber
- Contract schema updates for embeddings

### hauski-audio, sichter
- Standard template updates

## Verification After Application

After applying a patch, verify the changes:

```bash
# Check file changes
git status
git diff

# Run linters/tests (if available)
just lint
just test

# Check WGX validation
wgx validate
```

## Troubleshooting

### Patch doesn't apply cleanly

If you encounter conflicts when applying a patch:

```bash
# Try 3-way merge
git apply --3way reports/patches/<repo-name>.patch

# Or apply with reject files
git apply --reject reports/patches/<repo-name>.patch
# Then manually edit .rej files and resolve conflicts
```

### Empty or missing patch

Some repositories may not need updates. Check the patch file:

```bash
ls -lh reports/patches/<repo-name>.patch
```

If the patch is empty (0 bytes) or doesn't exist, the repository is already in sync with metarepo templates.

### Authentication issues with automated workflow

The workflow requires:
- `HEIMGEWEBE_APP_ID` secret
- `HEIMGEWEBE_APP_PRIVATE_KEY` secret

These should be configured in the metarepo repository settings under Secrets and variables → Actions.

**GitHub App Permissions**: The App should have minimal required permissions:
- Repository: Contents (read & write) and Pull Requests (read & write)
- Access limited to the specific fleet repositories

## Regenerating Patches

To regenerate patches after template updates in metarepo:

```bash
cd metarepo
./generate_patches.sh
```

This script will:
1. Clone or update external repository copies
2. Apply canonical templates from `templates/`
3. Generate new patch files in `reports/patches/`

## Workflow Configuration

The automated application workflow (`.github/workflows/apply-fleet-patches.yml`) uses:

- **Strategy**: Matrix parallelization for all fleet repos
- **Authentication**: GitHub App token with repo-specific access
- **Concurrency**: Each repo processed independently
- **Error handling**: `fail-fast: false` to continue even if one repo fails
- **PR creation**: Automatic with standardized title and description

## Related Documentation

- [AGENTS.md](../AGENTS.md): Metarepo reconciliation strategy and guidelines
- [templates/](../templates/): Canonical template source files
- [contracts/](../contracts/): Contract schema definitions
- [.github/workflows/apply-fleet-patches.yml](../.github/workflows/apply-fleet-patches.yml): Automated application workflow implementation

## Support

For issues or questions:
1. Check the patch application logs in GitHub Actions
2. Review the generated patch file for unexpected changes
3. Consult the metarepo team or create an issue

## Best Practices

1. **Always test first**: Use dry-run mode before applying patches
2. **Review PRs carefully**: Even automated changes should be reviewed
3. **Apply incrementally**: If unsure, apply to one repo first, then expand
4. **Keep templates updated**: Regularly sync templates from metarepo
5. **Document deviations**: If a repo needs to deviate from templates, document why
