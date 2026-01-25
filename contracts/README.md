# Heimgewebe Contracts

This directory contains the canonical JSON Schema definitions for the Heimgewebe fleet. These contracts are the **Single Source of Truth (SSOT)** for all data exchange between services.

## Canonical URIs

The canonical base URI for all schemas is `https://schemas.heimgewebe.org/`. While this domain may not be operational for hosting, it serves as the stable identifier for validation and referencing.

## Migration to Draft 2020-12

All new contracts **MUST** use JSON Schema Draft 2020-12. Legacy contracts using older drafts (e.g. Draft 07) remain valid until explicitly migrated.

## Usage Guidelines

**DO NOT** copy or embed these schemas into your service's source code directly. Doing so leads to drift and validation errors.

### Correct Usage

1.  **NPM Package**: Use the `@heimgewebe/contracts` package if your service is node-based.
    *   **Note**: `metarepo/contracts` is the **SSOT** (canonical source). The `@heimgewebe/contracts` package is a **distribution artifact** built from this source.
    *   **Publishing**: The package manifest in this directory exists for local validation and structure definition. Actual publishing to a registry is handled by the CI/Release pipeline (e.g. from a separate build step).
    *   Install via your package manager (e.g., `pnpm`, `npm`):
    ```bash
    npm install @heimgewebe/contracts
    ```
    Import schemas from `node_modules/@heimgewebe/contracts/contracts/...` or use the helper:
    ```js
    const { contractsPath } = require('@heimgewebe/contracts');
    const schemaPath = path.join(contractsPath, 'chronik/event.batch.v1.schema.json');
    ```

2.  **Vendoring (Automated)**: If you must vendor (e.g., non-JS services), use a script to download the specific version from the `metarepo` release artifacts.
    *   **Strict Rule**: Vendoring **MUST** be automated and pinned (e.g., via Release Tag or Commit SHA + SHA256 verification). Do NOT blindly fetch from `main`.
    *   Manual copying is prohibited to prevent semantic drift.

3.  **Reference**: Use absolute canonical URIs (e.g., `https://schemas.heimgewebe.org/...`) when referencing schemas in `consumers.yaml` or other contracts.
    *   `schema_ref` in events/artifacts **MUST** match the canonical `$id` of the referenced schema (e.g., the artifact schema or event schema).

## Governance Metadata

Governance metadata files are **NOT** JSON Schemas and are excluded from schema validation.

*   `contracts/meta/`: Detailed governance definitions.
*   `contracts/consumers.yaml`: Registry of contract consumption (producers/consumers).

## Structure

*   `events/`: Event envelopes and specific event type definitions.
*   `plexer/`: Contracts related to the Plexer routing service.
*   `heimlern/`: Contracts for Heimlern ingestion and state.
*   `chronik/`: Contracts for Chronik event storage and batch retrieval.
*   `integrity/`: Contracts for system integrity reporting.
*   `knowledge/`: Contracts for the Knowledge Observatory.

## Validation

All schemas must be valid JSON Schema Draft 2020-12. Changes are validated via CI using `ajv-cli`.

## Conventions

- **SHA-256**: Must be formatted as `sha256:<64-hex-chars>`. Pattern: `^sha256:[a-f0-9]{64}$`.

## Schema Versioning & Breaking Changes

### Major-Versioning for Schemas (SemVer major-only)

Schema versions (e.g., `v1`, `v2`) use major-only versioning adapted from semantic versioning principles:

- **v1 = Stable**: Once a schema reaches `v1`, it should remain backward compatible. Adding new optional fields is acceptable, but making existing optional fields required is a **breaking change**.
- **Version Format**: Schemas use major version numbers in filenames (e.g., `*.v1.schema.json`, `*.v2.schema.json`). Minor/patch versions do not exist as separate files—all changes within a major version (e.g., v1) must maintain backward compatibility.
- **Breaking Changes**: Require a new major version (e.g., `v2`). Examples include:
  - Adding new required fields to existing schemas
  - Changing field types or constraints
  - Removing fields
  - Removing or renaming enum values (breaking)
  - Adding new enum values (potentially breaking, depending on consumer strictness)

### Rollout Strategy for Schema Changes

When introducing enhanced validation (e.g., making optional fields required):

1. **Path A (Recommended)**: Create a new version (e.g., `*.v2.schema.json`)
   - Keep `v1` unchanged for backward compatibility
   - Producers upgrade to emit `v2` events
   - Consumers update to accept both `v1` and `v2`
   - Deprecate `v1` after fleet-wide adoption

2. **Path B (Fleet Cutover)**: Tighten existing schema with coordinated rollout
   - **Step 1**: Update all producers to emit new required fields
   - **Step 2**: Wait for confirmation that all producers are deployed
   - **Step 3**: Update schema to make fields required
   - **Step 4**: Update consumers/validators to enforce new requirements
   - **Risk**: High coordination overhead, potential for silent failures

**Recommended**: Use Path A (new version) to minimize risk and maintain clear migration paths.

### Optional vs Required Fields

Fields like `sha` and `schema_ref` in v1 published events are intentionally **optional** to accommodate gradual producer adoption:

- **Intent**: These fields SHOULD be present for integrity and traceability, but producers may not yet emit them reliably.
- **Migration Path**: Once all producers consistently emit these fields, consider introducing v2 schemas with stricter validation (making them required).
- **Consumer Guidance**: Consumers SHOULD handle missing optional fields gracefully but MAY log warnings to encourage producer updates.
