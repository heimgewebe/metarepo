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
