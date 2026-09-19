from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_DIR = ROOT / "scripts" / "contracts"
if str(VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_DIR))

from validate_consumers import RegistryError, validate_registry  # noqa: E402


def _fixture_root(directory: str) -> Path:
    target = Path(directory) / "repo"
    shutil.copytree(ROOT / "contracts", target / "contracts")
    return target


def _load_registry(root: Path) -> dict[str, object]:
    return yaml.safe_load((root / "contracts" / "consumers.yaml").read_text(encoding="utf-8"))


def _write_registry(root: Path, registry: dict[str, object]) -> None:
    (root / "contracts" / "consumers.yaml").write_text(
        yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _load_evidence(root: Path) -> dict[str, object]:
    return json.loads(
        (root / "contracts" / "consumer-evidence.v1.json").read_text(encoding="utf-8")
    )


def _write_evidence(root: Path, evidence: dict[str, object]) -> None:
    (root / "contracts" / "consumer-evidence.v1.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _claim(evidence: dict[str, object], claim_id: str) -> dict[str, object]:
    return next(item for item in evidence["claims"] if item["id"] == claim_id)


def _contract_evidence(evidence: dict[str, object], contract_id: str) -> dict[str, object]:
    return next(item for item in evidence["contracts"] if item["id"] == contract_id)


def test_current_registry_is_valid_and_evidence_bound() -> None:
    summary = validate_registry(ROOT)

    assert summary == {"contracts": 23, "claims": 50, "repositories": 11}


def test_active_contract_with_missing_schema_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        registry = _load_registry(root)
        registry["event_backbone"]["aussen.event"]["schema"] = (
            "contracts/missing-active.schema.json"
        )
        _write_registry(root, registry)

        with pytest.raises(RegistryError, match="active or compatibility schema is missing"):
            validate_registry(root)


def test_verified_claim_without_files_and_evidence_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        claim_id = "event_backbone/aussen.event::consumer::chronik"
        registry = _load_registry(root)
        consumer = next(
            item
            for item in registry["event_backbone"]["aussen.event"]["consumers"]
            if item["repo"] == "chronik"
        )
        consumer["files"] = []
        _write_registry(root, registry)

        evidence = _load_evidence(root)
        claim = _claim(evidence, claim_id)
        claim["files"] = []
        claim["evidence"] = []
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="requires files and evidence"):
            validate_registry(root)


def test_verified_mirror_with_wrong_hash_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        registry = _load_registry(root)
        consumer = next(
            item
            for item in registry["event_backbone"]["aussen.event"]["consumers"]
            if item["repo"] == "chronik"
        )
        consumer["mode"] = "mirror"
        consumer["status"] = "verified"
        consumer["files"] = ["contracts/aussen.event.schema.json"]
        _write_registry(root, registry)

        evidence = _load_evidence(root)
        claim = _claim(
            evidence,
            "event_backbone/aussen.event::consumer::chronik",
        )
        claim["mode"] = "mirror"
        claim["status"] = "verified"
        claim["files"] = ["contracts/aussen.event.schema.json"]
        claim["mirrorChecks"] = [
            {
                "path": "contracts/aussen.event.schema.json",
                "exists": True,
                "sha256": "0" * 64,
                "matches_canonical": True,
            }
        ]
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="differs from canonical schema"):
            validate_registry(root)


def test_claim_commit_must_match_audited_scope_commit() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        evidence = _load_evidence(root)
        claim = _claim(
            evidence,
            "knowledge/insights.daily::producer::semantAH",
        )
        claim["commit"] = "0" * 40
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="is not bound to scope commit"):
            validate_registry(root)


def test_replacement_must_resolve_to_registered_contract() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        registry = _load_registry(root)
        registry["knowledge"]["insights.daily.published"]["replacement"] = (
            "knowledge/missing-replacement"
        )
        _write_registry(root, registry)

        evidence = _load_evidence(root)
        _contract_evidence(
            evidence,
            "knowledge/insights.daily.published",
        )["replacement"] = "knowledge/missing-replacement"
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="replacement identities missing"):
            validate_registry(root)

def test_claim_status_must_match_contract_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        registry = _load_registry(root)
        producer = registry["policy"]["decision"]["producers"][0]
        producer["status"] = "verified"
        _write_registry(root, registry)

        evidence = _load_evidence(root)
        claim = _claim(evidence, "policy/decision::producer::heimlern")
        claim["status"] = "verified"
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="status conflicts with lifecycle historical"):
            validate_registry(root)


def test_evidence_must_cover_every_declared_repository() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = _fixture_root(directory)
        evidence = _load_evidence(root)
        evidence["scope"]["completeForDeclaredRepositories"] = False
        _write_evidence(root, evidence)

        with pytest.raises(RegistryError, match="must cover every declared repository"):
            validate_registry(root)



def test_aussen_event_schema_producers_match_audited_registry() -> None:
    schema = json.loads((ROOT / "contracts" / "aussen.event.schema.json").read_text(encoding="utf-8"))
    registry = _load_registry(ROOT)
    producers = [item["repo"] for item in registry["event_backbone"]["aussen.event"]["producers"]]

    assert schema["x-producers"] == producers == []



def test_event_line_schema_producers_match_audited_registry() -> None:
    schema = json.loads((ROOT / "contracts" / "event.line.schema.json").read_text(encoding="utf-8"))
    registry = _load_registry(ROOT)
    producer_claims = registry["event_backbone"]["event.line"]["producers"]
    producers = [item["repo"] for item in producer_claims]

    assert schema["x-producers"] == producers == []
    assert producer_claims == []

def _deleted_repository_names() -> set[str]:
    evidence = json.loads(
        (ROOT / "reports/fleet/physical-deletion-evidence.v1.json").read_text(encoding="utf-8")
    )
    return {item["name"] for item in evidence["deleted_repositories"]}


def test_active_registry_has_no_claims_for_deleted_repositories() -> None:
    registry = _load_registry(ROOT)
    deleted = _deleted_repository_names()
    offenders = []
    for category, entries in registry.items():
        for contract_name, contract in entries.items():
            if contract["lifecycle"] != "active":
                continue
            for key in ("producers", "consumers"):
                for claim in contract.get(key, []):
                    if claim["repo"] in deleted:
                        offenders.append((f"{category}/{contract_name}", key, claim["repo"]))
    assert offenders == []


def test_shared_schema_party_metadata_excludes_deleted_repositories() -> None:
    deleted = _deleted_repository_names()
    offenders = []
    for path in sorted((ROOT / "contracts").rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        for field in ("x-producers", "x-consumers"):
            values = payload.get(field)
            if isinstance(values, list):
                hits = sorted(deleted.intersection(value for value in values if isinstance(value, str)))
                if hits:
                    offenders.append((str(path.relative_to(ROOT)), field, hits))
    assert offenders == []


def test_contract_sync_does_not_target_deleted_repositories() -> None:
    deleted = _deleted_repository_names()
    script = (ROOT / "scripts/contracts-sync.sh").read_text(encoding="utf-8")
    for name in deleted:
        assert f"  {name}:" not in script
