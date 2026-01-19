# Heimgewebe Contracts

This directory contains the canonical JSON Schema definitions for the Heimgewebe fleet. These contracts are the **Single Source of Truth (SSOT)** for all data exchange between services.

## Canonical URIs

The canonical base URI for all schemas is `https://schemas.heimgewebe.org/`. While this domain may not be operational for hosting, it serves as the stable identifier for validation and referencing.

## Usage Guidelines

**DO NOT** copy or embed these schemas into your service's source code directly. Doing so leads to drift and validation errors.

### Correct Usage

1.  **NPM Package**: Use the `@heimgewebe/contracts` package if your service is node-based.
    ```bash
    npm install @heimgewebe/contracts
    ```
    Import schemas from `node_modules/@heimgewebe/contracts/contracts/...` or use the helper:
    ```js
    const { contractsPath } = require('@heimgewebe/contracts');
    const schemaPath = path.join(contractsPath, 'chronik/event.batch.v1.schema.json');
    ```

2.  **Vendoring (Automated)**: If you must vendor (e.g., non-JS services), use a script to download the specific version from the `metarepo` release artifacts or raw content. Ensure this process is automated and checks for updates.

3.  **Reference**: Use absolute canonical URIs (e.g., `https://schemas.heimgewebe.org/...`) when referencing schemas in `consumers.yaml` or other contracts.

## Structure

*   `events/`: Event envelopes and specific event type definitions.
*   `plexer/`: Contracts related to the Plexer routing service.
*   `heimlern/`: Contracts for Heimlern ingestion and state.
*   `chronik/`: Contracts for Chronik event storage and batch retrieval.
*   `integrity/`: Contracts for system integrity reporting.
*   `knowledge/`: Contracts for the Knowledge Observatory.

## Validation

All schemas must be valid JSON Schema Draft 2020-12. Changes are validated via CI using `ajv-cli`.
