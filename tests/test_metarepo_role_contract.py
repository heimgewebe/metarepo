from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROLE_PATH = ROOT / "system" / "metarepo-role.v1.json"


def load_role() -> dict[str, object]:
    return json.loads(ROLE_PATH.read_text(encoding="utf-8"))


def test_role_contract_has_expected_identity_and_scope() -> None:
    role = load_role()

    assert role["schema_version"] == 1
    assert role["kind"] == "metarepo_role"
    assert role["id"] == "repo:metarepo"
    assert role["status"] == "active"

    owned_domains = {item["domain"] for item in role["owns"]}
    assert owned_domains == {
        "fleet_membership",
        "shared_contracts",
        "shared_templates",
        "reusable_workflows",
    }

    delegated_domains = {
        item["domain"]: item["owner"] for item in role["does_not_own"]
    }
    assert delegated_domains == {
        "ecosystem_system_catalog": "repo:systemkatalog",
        "task_and_completion_truth": "repo:bureau",
        "operator_execution": "repo:grabowski",
        "runtime_health": "responsible_runtime",
        "ecosystem_history": "repo:chronik",
    }


def test_all_local_contract_paths_exist() -> None:
    role = load_role()

    for item in role["owns"]:
        assert (ROOT / item["authoritative_source"]).exists()

    for item in role["compatibility_surfaces"]:
        assert (ROOT / item["path"]).exists()

    for path in role["non_authoritative_legacy_documents"]:
        assert (ROOT / path).exists()

    for path in role["entrypoints"].values():
        assert (ROOT / path).exists()


def test_entrypoints_express_the_same_role_boundary() -> None:
    role = load_role()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    ai_context_text = (ROOT / ".ai-context.yml").read_text(encoding="utf-8")
    ai_context = yaml.safe_load(ai_context_text)

    role_path = role["entrypoints"]["normative_role_contract"]
    assert role_path in readme
    assert role_path in agents
    assert ai_context["documentation"]["role_contract"] == role_path
    assert ai_context["contracts"]["role_contract"]["path"] == role_path

    assert ai_context["project"]["role"] == "shared_asset_registry"
    assert ai_context["heimgewebe"]["fleet"]["authoritative_source"] == (
        "fleet/repos.yml"
    )

    assert "# Metarepo – Heimgewebe Control Plane" not in readme
    assert "role: control_plane" not in ai_context_text
    assert "zentraler, lernender Meta-Layer" not in agents


def test_legacy_surfaces_are_explicitly_non_normative() -> None:
    role = load_role()
    compatibility = {item["path"]: item for item in role["compatibility_surfaces"]}

    for item in compatibility.values():
        assert item["authoritative"] is False

    dispatcher = compatibility[
        ".github/workflows/heimgewebe-command-dispatch.yml"
    ]
    assert dispatcher["status"] == "compatibility_active"
    assert dispatcher["removal_gate"]


def test_role_contract_records_verification_limits() -> None:
    verification = load_role()["verification"]

    assert verification["last_verified_against_commit"] == (
        "4777fd5cfafea22813f9c3d647b33a0ffefd994b"
    )
    assert verification["does_not_establish"]
