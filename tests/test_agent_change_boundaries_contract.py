from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts/operator/agent-change-boundaries.v1.json"
INVENTORY_PATH = ROOT / "docs/archive/leitwerk-normative-freeze.v1.json"
ROLE_PATH = ROOT / "system/metarepo-role.v1.json"

SOURCE_REPOSITORY = "heimgewebe/leitwerk"
SOURCE_COMMIT = "c241244d8e7613f6d4eaff7a6686c841444f1ade"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_agent_change_contract_has_bounded_identity_and_principles() -> None:
    contract = load_json(CONTRACT_PATH)

    assert contract["schema_version"] == 1
    assert contract["kind"] == "agent_change_boundaries"
    assert contract["status"] == "active"
    assert contract["authority"] == {
        "owner": "repo:metarepo",
        "domain": "shared_contracts",
        "source": "contracts/operator/agent-change-boundaries.v1.json",
    }

    principle_ids = {item["id"] for item in contract["principles"]}
    assert principle_ids == {
        "proposal-not-effect",
        "isolated-repository-change",
        "gate-precedence",
        "evidence-bound-effect",
        "ambiguous-outcome-fails-closed",
        "material-uncertainty-explicit",
    }


def test_contract_delegates_current_truth_and_inherits_no_leitwerk_authority() -> None:
    contract = load_json(CONTRACT_PATH)

    owners = {
        item["domain"]: item["owner"] for item in contract["truth_ownership"]
    }
    assert owners == {
        "tasks_claims_completion": "repo:bureau",
        "local_execution_leases_recovery": "repo:grabowski",
        "repositories_branches_pull_requests_reviews": "github",
        "technical_checks": "ci_and_repository_gates",
        "ecosystem_semantics": "repo:systemkatalog",
        "event_history": "repo:chronik",
    }
    assert all("leitwerk" not in owner.lower() for owner in owners.values())

    exclusions = set(contract["does_not_establish"])
    assert {
        "leitwerk_runtime_authority",
        "leitwerk_policy_authority",
        "leitwerk_task_or_claim_authority",
        "automatic_authority_transfer_to_bureau",
        "automatic_authority_transfer_to_grabowski",
        "automatic_authority_transfer_to_konvergenzregelkreis",
    }.issubset(exclusions)


def test_freeze_inventory_is_digest_bound_and_complete() -> None:
    inventory = load_json(INVENTORY_PATH)

    assert inventory["source"] == {
        "repository": SOURCE_REPOSITORY,
        "commit": SOURCE_COMMIT,
        "default_branch": "main",
        "open_pull_requests": 0,
    }

    files = inventory["files"]
    assert len(files) == 40
    assert len({item["path"] for item in files}) == 40
    assert all(len(item["sha256"]) == 64 for item in files)
    assert all(
        set(item["sha256"]).issubset(set("0123456789abcdef"))
        for item in files
    )

    counts = inventory["counts"]
    assert counts["files"] == len(files)
    assert counts["keep"] == sum(item["decision"] == "keep" for item in files)
    assert counts["migrate"] == sum(
        item["decision"] == "migrate" for item in files
    )
    assert counts["retire"] == sum(item["decision"] == "retire" for item in files)
    assert set(item["decision"] for item in files) == {"keep", "migrate", "retire"}


def test_migration_scope_matches_contract_provenance() -> None:
    contract = load_json(CONTRACT_PATH)
    inventory = load_json(INVENTORY_PATH)

    migrated_paths = {
        item["path"] for item in inventory["files"] if item["decision"] == "migrate"
    }
    assert migrated_paths == set(
        contract["legacy_migration"]["migrated_semantic_sources"]
    )
    assert contract["legacy_migration"]["source_repository"] == SOURCE_REPOSITORY
    assert contract["legacy_migration"]["source_commit"] == SOURCE_COMMIT
    assert contract["legacy_migration"]["source_inventory"] == (
        "docs/archive/leitwerk-normative-freeze.v1.json"
    )


def test_legacy_schemas_and_guards_are_terminally_classified() -> None:
    inventory = load_json(INVENTORY_PATH)

    schema_classification = inventory["schema_classification"]
    assert schema_classification["decision"] == "retire_legacy_phase1_suite"
    assert "artifact.header.v1.schema.json" in "\n".join(
        schema_classification["paths"]
    )

    guard_decisions = {
        item["path"]: item["decision"] for item in inventory["guard_classification"]
    }
    assert guard_decisions == {
        ".github/workflows/guard-branch-only.yml": "retire_on_archive",
        ".github/workflows/guard-contracts-mirror.yml": "retire_on_archive",
        "scripts/guard_contracts_mirror.sh": "retire_on_archive",
        "scripts/test_guard_contracts_mirror_functions.sh": "retire_on_archive",
        "github-default-codeql": "ceases_with_repository_archive",
    }


def test_metarepo_role_registers_the_active_shared_contract() -> None:
    role = load_json(ROLE_PATH)

    entries = {
        item["path"]: item for item in role["active_shared_contracts"]
    }
    assert entries["contracts/operator/agent-change-boundaries.v1.json"] == {
        "path": "contracts/operator/agent-change-boundaries.v1.json",
        "scope": "provider-neutral boundary between agent proposals and effects",
        "provenance": f"{SOURCE_REPOSITORY}@{SOURCE_COMMIT}",
        "inventory": "docs/archive/leitwerk-normative-freeze.v1.json",
    }
