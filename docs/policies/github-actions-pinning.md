# GitHub Actions Pinning Policy

To ensure security, stability, and reproducibility of our CI/CD pipelines, we enforce strict version pinning for all GitHub Actions.

## Policy

1.  **Pin by Tag or Commit SHA**: All `uses:` directives in workflow files must reference a specific version tag (e.g., `@v2`, `@v1.2.3`) or a full commit SHA.
2.  **No `@main` or `@master`**: References to mutable branch names like `@main` or `@master` are prohibited. This prevents upstream changes from breaking our builds unexpectedly or introducing malicious code.

## Critical reusable workflows

The reusable `heimgewebe-command-dispatch.yml` workflow is a privileged
organization-wide control path. Every external `uses:` reference inside that
workflow must use a full 40-character commit SHA. Major tags remain acceptable
elsewhere under the general policy, but not inside the command dispatcher.

## Verification

The `check-action-refs` job enforces both layers: the repository-wide prohibition on branch refs and the commit-only rule for the command dispatcher.

## Exceptions

There is currently one authorized exception to this policy:

-   **Workflow**: `heimgewebe/metarepo/.github/workflows/heimgewebe-command-dispatch.yml@main`
-   **Usage**: Used in `pr-heimgewebe-commands.yml`.
-   **Reason**: This workflow is part of the internal metarepo dispatch mechanism. Using `@main` ensures that the dispatch logic is always up-to-date with the latest implementation in the metarepo, avoiding the need to manually update tags across all repositories when the dispatch logic changes. Since this is an internal reference within the same trusted organization, the security risk is mitigated.
