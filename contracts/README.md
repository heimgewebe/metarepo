# Shared Contracts

Metarepo owns the shared schema files stored below `contracts/`. Those files are the canonical byte definitions for the contracts they publish. Metarepo does **not** own the runtime state, delivery success or semantic correctness of producing and consuming systems.

## Machine-readable governance

- `consumers.yaml` is the backward-compatible registry of known contracts, lifecycle state, replacement targets and reviewed producer/consumer claims.
- `consumer-evidence.v1.json` binds those claims to exact default-branch commits, repository paths, line references and, for verified mirrors, byte hashes.
- `scripts/contracts/validate_consumers.py` checks both files fail-closed.

Lifecycle values:

- `active`: the schema is maintained as a current shared contract.
- `compatibility`: the contract remains for a bounded migration or compatibility surface.
- `historical`: the entry is retained for audit and must not be used as evidence of an active route.

Claim status values:

- `verified`: the exact audited repository commit contains path evidence; mirror claims additionally require byte identity.
- `unverified`: the relationship remains a review target and is not established as current.
- `compatibility`: only a bounded compatibility relationship is asserted.
- `historical`: the relationship is retained solely as historical evidence.

A `verified` claim proves repository coupling at the audited commit. It does not prove live runtime use, runtime health, delivery success, semantic correctness or future compatibility. The current evidence set covers the repositories already declared in `consumers.yaml`; it does not claim complete organization-wide discovery.

## Validation

```bash
uv run python scripts/contracts/validate_consumers.py
uv run pytest -q tests/test_contract_consumers_registry.py
scripts/validate-contracts.sh
```
