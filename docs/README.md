# Metarepo Documentation

Welcome to the Heimgewebe Metarepo documentation!

## Core Documentation

### Architecture & Vision
- [Architecture](system/architecture.md): System overview and component layers
- [Vision](vision/vision.md): Guidelines and roadmap
- [Konzept Kern](konzept-kern.md): Core concepts - Governance, Sync, Drift (German)
- [Nutzung](nutzung.md): Usage & Daily Operations (German)

### Fleet Management
- [Fleet](fleet/fleet.md): Template synchronization and fleet operations
- [Push to Fleet](fleet/push-to-fleet.md): Fleet deployment procedures
- [Repo Matrix](repo-matrix.md): Repository roles and status
- [Templates](templates.md): Template distribution and drift management
- [Automation](policies/automation.md): CI/CD and automation patterns
- [CI Reusables](policies/ci-reusables.md): Reusable workflow patterns

### Contracts & APIs
- [Contract Versioning](contracts/contract-versioning.md): Rollout process
- [Knowledge Contracts](knowledge-contracts.md): Knowledge graph contracts
- [Contracts Overview](contracts/contracts-index.md): Contract index
- [API](api.md): API documentation

#### Contract Details
- [Mitschreiber Contract](contracts/mitschreiber.md): Intent and context events
- [Sichter Contract](contracts/sichter.md): Review and diagnostic events

### Development
- [WGX Konzept](fleet/wgx-konzept.md): Fleet motor and commands
- [WGX Stub](wgx-stub.md): WGX stub implementation
- [Agents](agents.md): Guidelines for AI agents
- [Environment](fleet/environment.md): Development environment setup
- [E2E](runbooks/e2e.md): End-to-end testing
- [Troubleshooting](runbooks/troubleshooting.md): Common issues and solutions
- [Runbooks](runbooks/runbooks.md): Operational runbooks
- [Graph](graph.md): Dependency analysis

### Process & Guidelines
- [Leitlinien](leitlinien.md): Development guidelines (German)
- [Language Guide](language-guide.md): Bilingual documentation strategy
- [Architecture Decision Records (ADRs)](adrs/README.md): Design decisions and rationale
- [Policies](policies/orientierung.md): General policies and orientation
- [GitHub Actions Pinning](policies/github-actions-pinning.md): Action versioning policy
- [Repos.yml Documentation](repos.yml.md): Fleet configuration reference

### Vision & Planning
- [Vision Overview](vision/README.md): Vision documents overview
- [Heimgewebe Evolution](vision/heimgewebe-evolution-maximaleffizienz.md): System evolution strategy
- [Heimgewebe v2 Detailed](vision/heimgewebe-v2-detailed.md): Detailed v2 roadmap

### System Documentation
- [Heimgeist vs HausKI](system/heimgeist_vs_hauski.md): Component comparison
- [IDEal Blueprint](vision/IDEal_Blueprint.md): IDE integration blueprint
- [System Organism](system/heimgewebe-organismus.md): Organism model
- [System Target State](system/heimgewebe-zielbild.md): Target state definition

## Tools Documentation

The following documentation relates to tools used by this repository:

### Just Task Runner
- [Just Commands](tools/just.md): Just task runner overview

### actionlint (GitHub Actions Linter)
- [actionlint Checks](policies/checks.md): GitHub Actions linting (actionlint tool)
- [actionlint Installation](runbooks/install.md): Tool installation (actionlint)
- [actionlint Usage](runbooks/usage.md): Tool usage (actionlint)
- [actionlint Configuration](config.md): Tool configuration (actionlint)
- [actionlint References](reference.md): Additional resources (actionlint)

## Quick Links

- Main README: [../README.md](../README.md)
- Contributing Guide: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- Agents Guide: [../AGENTS.md](../AGENTS.md)
