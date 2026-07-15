from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROLE_PATH = ROOT / "system" / "metarepo-role.v1.json"


def load_role() -> dict[str, object]:
    return json.loads(ROLE_PATH.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        metadata_source = item.get("metadata_source")
        if metadata_source:
            assert (ROOT / metadata_source).exists()

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

    repos_projection = compatibility["repos.yml"]
    assert repos_projection["status"] == "compatibility_generated"
    assert repos_projection["generated_from"] == [
        "fleet/repos.yml",
        "fleet/repo-metadata.yml",
    ]

    dispatcher = compatibility[
        ".github/workflows/heimgewebe-command-dispatch.yml"
    ]
    assert dispatcher["status"] == "compatibility_active"
    assert dispatcher["removal_gate"]


def test_architecture_sources_delegate_ecosystem_semantics() -> None:
    role = load_role()
    sources = role["architecture_sources"]

    assert sources["repository_role"] == {
        "owner": "repo:metarepo",
        "path": "system/metarepo-role.v1.json",
    }

    ecosystem = sources["ecosystem_semantics"]
    assert ecosystem["owner"] == "repo:systemkatalog"
    assert ecosystem["rendered_path"] == "rendered/system-catalog.md"
    assert ecosystem["inventory_path"] == "registry/ecosystem/nodes.json"
    assert ecosystem["authority_matrix_path"] == (
        "registry/ecosystem/authority-matrix.v1.json"
    )
    assert ecosystem["verified_commit"] == (
        "ac0e7cc8862c97125862b1475068832d8d517475"
    )


def test_legacy_archive_manifest_binds_unchanged_originals() -> None:
    role = load_role()
    policy = role["legacy_document_policy"]

    assert policy["status"] == "historical_non_normative"
    assert policy["valid_through"] == "2026-07-14"
    assert policy["superseded_on"] == "2026-07-15"
    assert policy["compatibility_paths_preserved"] is True

    manifest_path = ROOT / policy["archive_manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "historical_non_normative"
    assert manifest["archived_from_commit"] == (
        "0a0f6ddd25aeb634dbee7060c650923fe7b709ea"
    )
    assert manifest["current_sources"]["system_catalog_verified_commit"] == (
        "ac0e7cc8862c97125862b1475068832d8d517475"
    )

    archive_root = ROOT / policy["archive_root"]
    for item in manifest["files"]:
        archived = archive_root / item["archive_path"]
        assert archived.is_file()
        assert file_sha256(archived) == item["sha256"]
        assert (ROOT / item["former_path"]).exists()


def test_legacy_compatibility_pages_cannot_pose_as_current_architecture() -> None:
    role = load_role()
    primary_markdown = [
        "docs/system/heimgewebe-organismus.md",
        "docs/system/heimgewebe-zielbild.md",
        "docs/system/architecture.md",
        "docs/vision/vision.md",
        "docs/vision/heimgewebe-capability-plan.md",
        "docs/roadmaps/heimgewebe-capabilities-2026.md",
        "docs/architecture/integrity-neurose.md",
        "docs/architecture/pipeline-channels.md",
        "docs/system/plexer-eventmodel.md",
        "docs/system/heimgeist_vs_hauski.md",
        "docs/vision/leitwerk-blueprint",
        "docs/vision/README.md",
        "heimgewebe/README.md",
        "heimgewebe/PROJECT.md",
    ]

    for relative in primary_markdown:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "historisch" in text.lower()
        assert "2026-07-14" in text
        assert "2026-07-15" in text
        assert "systemkatalog" in text.lower()

    for relative in [
        "docs/system/heimgewebe-architektur.mmd",
        "docs/system/heimgewebe-dataflow.mmd",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "historical_non_normative" in text
        assert "systemkatalog" in text.lower()

    for relative in [
        "docs/canvas/heimgewebe-architektur.canvas",
        "docs/canvas/heimgewebe-dataflow.canvas",
    ]:
        canvas = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        assert canvas["edges"] == []
        assert len(canvas["nodes"]) == 1
        notice = canvas["nodes"][0]["text"].lower()
        assert "historischer kompatibilitätspfad" in notice
        assert "nicht mehr aktuell" in notice
        assert "systemkatalog" in notice

    assert set(primary_markdown).issubset(
        set(role["non_authoritative_legacy_documents"])
    )


def test_documentation_index_does_not_present_legacy_model_as_current() -> None:
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    context = (ROOT / "docs" / "organismus-kontextblock.md").read_text(
        encoding="utf-8"
    )

    assert "Historical architecture and planning" in docs_readme
    assert "System Organism" not in docs_readme
    assert "Target state definition" not in docs_readme
    assert "Systemkatalog" in docs_readme
    assert "Systemkatalog" in context
    assert "Bureau" in context
    assert "Grabowski" in context
    assert "historisches Material" in context

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    vision_index = (ROOT / "docs" / "vision" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "bis zur gesonderten Historisierung" not in root_readme
    assert "hashgebunden" in root_readme
    assert "hashgebunden" in agents
    assert "historischer Index" in vision_index
    assert "Aktive Aufgaben und Reihenfolge: Bureau" in vision_index


def test_role_contract_records_projection_safety_invariants() -> None:
    invariants = load_role()["invariants"]

    assert any("bytegenau" in item and "repos.yml" in item for item in invariants)
    assert any("fleet: false" in item and "nicht" in item for item in invariants)
    assert any("hashgebundene" in item and "Archivmanifest" in item for item in invariants)
    assert any("Systemkatalog" in item and "nicht" in item for item in invariants)


def test_role_contract_records_verification_limits() -> None:
    verification = load_role()["verification"]

    assert verification["last_verified_at"] == "2026-07-15"
    assert verification["last_verified_against_commit"] == (
        "0a0f6ddd25aeb634dbee7060c650923fe7b709ea"
    )
    assert any(
        "ac0e7cc8862c97125862b1475068832d8d517475" in item
        for item in verification["evidence_scope"]
    )
    assert verification["does_not_establish"]
