# Metarepo Documentation

## Current role and source boundaries

Metarepo is a delivery repository for Fleet membership, shared contracts, curated templates and reusable workflows. It is not the system catalog or an ecosystem control plane.

- [Normative Metarepo role](../system/metarepo-role.v1.json)
- [Agent and operator guidance](../AGENTS.md)
- [Systemkatalog rendered view](https://github.com/heimgewebe/systemkatalog/blob/main/rendered/system-catalog.md)
- [Systemkatalog machine-readable inventory](https://github.com/heimgewebe/systemkatalog/blob/main/registry/ecosystem/nodes.json)
- [Source-of-truth context snippet](organismus-kontextblock.md)

Tasks, priorities and completion belong to Bureau. Execution, leases, audit and recovery belong to Grabowski. Historical events belong to Chronik. Runtime health belongs to each responsible service.

## Repository delivery documentation

### Fleet management

- [Fleet](fleet/fleet.md): template synchronization and fleet operations
- [Push to Fleet](fleet/push-to-fleet.md): Fleet deployment procedures
- [Repo Matrix](repo-matrix.md): legacy repository-role overview; verify against Systemkatalog before use
- [Templates](templates.md): template distribution and drift management
- [Automation](policies/automation.md): CI/CD and automation patterns
- [CI Reusables](policies/ci-reusables.md): reusable workflow patterns
- [Repos.yml Documentation](repos.yml.md): generated compatibility projection reference

### Contracts and APIs

- [Contract Versioning](contracts/contract-versioning.md): rollout process
- [Knowledge Contracts](knowledge-contracts.md): knowledge graph contracts
- [Contracts Overview](contracts/contracts-index.md): contract index
- [API](api.md): API documentation
- [Mitschreiber Contract](contracts/mitschreiber.md): intent and context events
- [Sichter Contract](contracts/sichter.md): review and diagnostic events

### Development and operations

- [WGX Konzept](fleet/wgx-konzept.md): Fleet motor and commands
- [WGX Stub](wgx-stub.md): WGX compatibility implementation
- [Agents](agents.md): guidelines for AI agents
- [Environment](fleet/environment.md): development environment setup
- [E2E](runbooks/e2e.md): end-to-end testing
- [Troubleshooting](runbooks/troubleshooting.md): common issues and solutions
- [Runbooks](runbooks/runbooks.md): operational runbooks
- [Graph](graph.md): dependency analysis

### Process and guidelines

- [Leitlinien](leitlinien.md): development guidelines
- [Language Guide](language-guide.md): bilingual documentation strategy
- [Architecture Decision Records](adrs/README.md): historical decisions and rationale
- [Policies](policies/orientierung.md): general policies and orientation
- [GitHub Actions Pinning](policies/github-actions-pinning.md): action versioning policy

## Historical architecture and planning

The former Organismus v0.2 model, target state, diagrams, vision and capability plans are preserved for provenance only:

- [Archive index](archive/heimgewebe-organismus-v0.2/README.md)
- [Hash-bound archive manifest](archive/heimgewebe-organismus-v0.2/manifest.v1.json)
- [Organism compatibility page](system/heimgewebe-organismus.md)
- [Target-state compatibility page](system/heimgewebe-zielbild.md)
- [Architecture compatibility page](system/architecture.md)
- [Vision compatibility page](vision/vision.md)
- [Capability-plan compatibility page](vision/heimgewebe-capability-plan.md)
- [Capability-roadmap compatibility page](roadmaps/heimgewebe-capabilities-2026.md)

These files are not current architecture, task or roadmap sources.

## Tool documentation

- [Just Commands](tools/just.md)
- [actionlint Checks](policies/checks.md)
- [actionlint Installation](runbooks/install.md)
- [actionlint Usage](runbooks/usage.md)
- [actionlint Configuration](config.md)
- [actionlint References](reference.md)

## Quick links

- [Main README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Agents Guide](../AGENTS.md)
