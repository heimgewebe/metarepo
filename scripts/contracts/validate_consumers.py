#!/usr/bin/env python3
"""Validate the evidence-bound Metarepo contract consumer registry."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "contracts/consumers.yaml"
EVIDENCE_PATH = ROOT / "contracts/consumer-evidence.v1.json"

LIFECYCLES = {"active", "compatibility", "historical"}
STATUSES = {"verified", "unverified", "compatibility", "historical"}
ROLES = {"producer", "consumer"}
MODES = {None, "mirror", "reference-only", "notification-only"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
REPO_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


class RegistryError(ValueError):
    """Raised when the registry or its evidence is inconsistent."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{label} must be a non-empty string")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RegistryError(f"{label} must be an array")
    return value


def _safe_relative_path(value: Any, label: str) -> str:
    text = _require_string(value, label)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise RegistryError(f"{label} must stay within its repository")
    return text


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _claim_ref(ref: Any, expected_id: str) -> None:
    expected = f"contracts/consumer-evidence.v1.json#claims/{expected_id}"
    if ref != expected:
        raise RegistryError(f"claim evidence_ref mismatch for {expected_id}")


def _contract_ref(ref: Any, expected_id: str) -> None:
    expected = f"contracts/consumer-evidence.v1.json#contracts/{expected_id}"
    if ref != expected:
        raise RegistryError(f"contract evidence_ref mismatch for {expected_id}")


def _validate_claim(
    *,
    identity: str,
    role: str,
    item: dict[str, Any],
    evidence_claims: dict[str, dict[str, Any]],
    repository_heads: dict[str, str],
    observed_at: str,
    schema_sha256: str | None,
) -> None:
    if role not in ROLES:
        raise RegistryError(f"unsupported role: {role}")
    repo = _require_string(item.get("repo"), f"{identity}.{role}.repo")
    if not REPO_NAME.fullmatch(repo):
        raise RegistryError(f"{identity}.{role}.{repo}.repo is invalid")
    status = item.get("status")
    if status not in STATUSES:
        raise RegistryError(f"{identity}.{role}.{repo}.status is invalid")
    mode = item.get("mode") if role == "consumer" else None
    if mode not in MODES:
        raise RegistryError(f"{identity}.{role}.{repo}.mode is invalid")
    if item.get("last_verified") != observed_at:
        raise RegistryError(f"{identity}.{role}.{repo}.last_verified differs from evidence")
    files = _require_list(item.get("files"), f"{identity}.{role}.{repo}.files")
    normalized_files = [
        _safe_relative_path(path, f"{identity}.{role}.{repo}.files") for path in files
    ]
    if len(normalized_files) != len(set(normalized_files)):
        raise RegistryError(f"{identity}.{role}.{repo}.files contains duplicates")

    claim_id = f"{identity}::{role}::{repo}"
    _claim_ref(item.get("evidence_ref"), claim_id)
    claim = evidence_claims.get(claim_id)
    if claim is None:
        raise RegistryError(f"evidence claim missing: {claim_id}")
    expected_repository = f"heimgewebe/{repo}"
    expected = {
        "contract": identity,
        "role": role,
        "repository": expected_repository,
        "status": status,
        "mode": mode,
        "files": normalized_files,
    }
    for key, value in expected.items():
        if claim.get(key) != value:
            raise RegistryError(f"evidence claim {claim_id} differs at {key}")
    commit = claim.get("commit")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        raise RegistryError(f"evidence claim {claim_id} has invalid commit")
    if repository_heads.get(expected_repository) != commit:
        raise RegistryError(f"evidence claim {claim_id} is not bound to scope commit")

    evidence_items = _require_list(claim.get("evidence"), f"{claim_id}.evidence")
    evidence_paths: list[str] = []
    for index, evidence in enumerate(evidence_items):
        if not isinstance(evidence, dict):
            raise RegistryError(f"{claim_id}.evidence[{index}] must be an object")
        path = _safe_relative_path(evidence.get("path"), f"{claim_id}.evidence[{index}].path")
        line = evidence.get("line")
        if not isinstance(line, int) or line < 1:
            raise RegistryError(f"{claim_id}.evidence[{index}].line must be positive")
        _require_string(evidence.get("kind"), f"{claim_id}.evidence[{index}].kind")
        evidence_paths.append(path)

    if status == "verified":
        if not normalized_files or not evidence_items:
            raise RegistryError(f"verified claim {claim_id} requires files and evidence")
        if mode != "mirror" and not set(normalized_files).issubset(set(evidence_paths)):
            raise RegistryError(f"verified claim {claim_id} files are not evidence-bound")

    if mode == "mirror" and status == "verified":
        checks = _require_list(claim.get("mirrorChecks"), f"{claim_id}.mirrorChecks")
        if not checks:
            raise RegistryError(f"verified mirror {claim_id} requires byte checks")
        checked_paths = set()
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                raise RegistryError(f"{claim_id}.mirrorChecks[{index}] must be an object")
            path = _safe_relative_path(
                check.get("path"), f"{claim_id}.mirrorChecks[{index}].path"
            )
            checked_paths.add(path)
            if check.get("exists") is not True or check.get("matches_canonical") is not True:
                raise RegistryError(f"verified mirror {claim_id} is not byte-identical")
            digest = check.get("sha256")
            if not isinstance(digest, str) or not SHA64.fullmatch(digest):
                raise RegistryError(f"verified mirror {claim_id} has invalid sha256")
            if schema_sha256 is not None and digest != schema_sha256:
                raise RegistryError(f"verified mirror {claim_id} differs from canonical schema")
        if not set(normalized_files).issubset(checked_paths | set(evidence_paths)):
            raise RegistryError(f"verified mirror {claim_id} lacks checks for declared files")


def validate_registry(root: Path = ROOT) -> dict[str, int]:
    registry_path = root / REGISTRY_PATH.relative_to(ROOT)
    evidence_path = root / EVIDENCE_PATH.relative_to(ROOT)
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RegistryError(f"cannot parse {registry_path}: {exc}") from exc
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot parse {evidence_path}: {exc}") from exc

    if not isinstance(registry, dict) or not registry:
        raise RegistryError("consumer registry must be a non-empty mapping")
    if evidence.get("schemaVersion") != 1 or evidence.get("kind") != "metarepo_contract_consumer_evidence":
        raise RegistryError("consumer evidence identity mismatch")
    observed_at = _require_string(evidence.get("observedAt"), "evidence.observedAt")
    try:
        parsed_observed_at = datetime.fromisoformat(observed_at)
    except ValueError as exc:
        raise RegistryError("evidence.observedAt must be an ISO-8601 timestamp") from exc
    if parsed_observed_at.tzinfo is None:
        raise RegistryError("evidence.observedAt must include a timezone")
    source = evidence.get("source")
    if not isinstance(source, dict):
        raise RegistryError("evidence.source must be an object")
    if source.get("repository") != "heimgewebe/metarepo":
        raise RegistryError("evidence source repository mismatch")
    if not isinstance(source.get("commit"), str) or not SHA40.fullmatch(source["commit"]):
        raise RegistryError("evidence source commit invalid")
    if not isinstance(source.get("auditFinalizationReceiptSha256"), str) or not SHA64.fullmatch(
        source["auditFinalizationReceiptSha256"]
    ):
        raise RegistryError("evidence audit receipt invalid")
    _require_string(source.get("auditJob"), "evidence.source.auditJob")
    _require_string(source.get("method"), "evidence.source.method")

    scope = evidence.get("scope")
    if not isinstance(scope, dict):
        raise RegistryError("evidence.scope must be an object")
    if scope.get("completeForDeclaredRepositories") is not True:
        raise RegistryError("evidence must cover every declared repository")
    if scope.get("completeForOrganization") is not False:
        raise RegistryError("evidence must not claim complete organization coverage")
    if not isinstance(scope.get("githubCodeSearchComplete"), bool):
        raise RegistryError("evidence.scope.githubCodeSearchComplete must be boolean")
    repository_heads: dict[str, str] = {}
    for index, repository in enumerate(_require_list(scope.get("repositories"), "scope.repositories")):
        if not isinstance(repository, dict):
            raise RegistryError(f"scope.repositories[{index}] must be an object")
        name = _require_string(repository.get("repository"), f"scope.repositories[{index}].repository")
        commit = repository.get("commit")
        if not isinstance(commit, str) or not SHA40.fullmatch(commit):
            raise RegistryError(f"scope.repositories[{index}].commit invalid")
        if name in repository_heads:
            raise RegistryError(f"duplicate scope repository: {name}")
        repository_heads[name] = commit

    evidence_contracts: dict[str, dict[str, Any]] = {}
    for item in _require_list(evidence.get("contracts"), "evidence.contracts"):
        if not isinstance(item, dict):
            raise RegistryError("evidence contract must be an object")
        identity = _require_string(item.get("id"), "evidence contract id")
        if identity in evidence_contracts:
            raise RegistryError(f"duplicate evidence contract: {identity}")
        evidence_contracts[identity] = item

    evidence_claims: dict[str, dict[str, Any]] = {}
    for item in _require_list(evidence.get("claims"), "evidence.claims"):
        if not isinstance(item, dict):
            raise RegistryError("evidence claim must be an object")
        claim_id = _require_string(item.get("id"), "evidence claim id")
        if claim_id in evidence_claims:
            raise RegistryError(f"duplicate evidence claim: {claim_id}")
        evidence_claims[claim_id] = item

    identities: set[str] = set()
    claim_count = 0
    for category, entries in registry.items():
        _require_string(category, "registry category")
        if not isinstance(entries, dict) or not entries:
            raise RegistryError(f"registry category {category} must be a non-empty mapping")
        for contract_name, item in entries.items():
            identity = f"{category}/{contract_name}"
            if identity in identities:
                raise RegistryError(f"duplicate contract identity: {identity}")
            identities.add(identity)
            if not isinstance(item, dict):
                raise RegistryError(f"{identity} must be an object")
            schema = _safe_relative_path(item.get("schema"), f"{identity}.schema")
            if not schema.startswith("contracts/"):
                raise RegistryError(f"{identity}.schema must stay below contracts/")
            lifecycle = item.get("lifecycle")
            if lifecycle not in LIFECYCLES:
                raise RegistryError(f"{identity}.lifecycle is invalid")
            if item.get("last_verified") != observed_at:
                raise RegistryError(f"{identity}.last_verified differs from evidence")
            _require_string(item.get("status_reason"), f"{identity}.status_reason")
            replacement = item.get("replacement")
            if replacement is not None:
                _require_string(replacement, f"{identity}.replacement")
            _contract_ref(item.get("evidence_ref"), identity)

            schema_path = root / schema
            schema_exists = schema_path.is_file()
            if lifecycle != "historical" and not schema_exists:
                raise RegistryError(f"{identity} active or compatibility schema is missing: {schema}")
            schema_digest = _sha256(schema_path) if schema_exists else None

            contract_evidence = evidence_contracts.get(identity)
            if contract_evidence is None:
                raise RegistryError(f"contract evidence missing: {identity}")
            expected_contract = {
                "schema": schema,
                "schemaExists": schema_exists,
                "schemaSha256": schema_digest,
                "lifecycle": lifecycle,
                "replacement": replacement,
            }
            for key, value in expected_contract.items():
                if contract_evidence.get(key) != value:
                    raise RegistryError(f"contract evidence {identity} differs at {key}")

            allowed_statuses = {
                "active": {"verified", "unverified"},
                "compatibility": {"compatibility"},
                "historical": {"historical"},
            }[lifecycle]
            for producer in _require_list(item.get("producers"), f"{identity}.producers"):
                if not isinstance(producer, dict):
                    raise RegistryError(f"{identity}.producer must be an object")
                if producer.get("status") not in allowed_statuses:
                    raise RegistryError(f"{identity}.producer status conflicts with lifecycle {lifecycle}")
                _validate_claim(
                    identity=identity,
                    role="producer",
                    item=producer,
                    evidence_claims=evidence_claims,
                    repository_heads=repository_heads,
                    observed_at=observed_at,
                    schema_sha256=schema_digest,
                )
                claim_count += 1
            for consumer in _require_list(item.get("consumers"), f"{identity}.consumers"):
                if not isinstance(consumer, dict):
                    raise RegistryError(f"{identity}.consumer must be an object")
                if consumer.get("status") not in allowed_statuses:
                    raise RegistryError(f"{identity}.consumer status conflicts with lifecycle {lifecycle}")
                _validate_claim(
                    identity=identity,
                    role="consumer",
                    item=consumer,
                    evidence_claims=evidence_claims,
                    repository_heads=repository_heads,
                    observed_at=observed_at,
                    schema_sha256=schema_digest,
                )
                claim_count += 1

    for identity, item in evidence_contracts.items():
        if identity not in identities:
            raise RegistryError(f"orphan evidence contract: {identity}")
    if set(evidence_claims) != {
        f"{identity}::{role}::{claim['repo']}"
        for category, entries in registry.items()
        for contract_name, contract in entries.items()
        for role, key in (("producer", "producers"), ("consumer", "consumers"))
        for claim in contract.get(key, [])
        for identity in [f"{category}/{contract_name}"]
    }:
        raise RegistryError("evidence claim coverage differs from registry")

    replacements = {
        item.get("replacement")
        for entries in registry.values()
        for item in entries.values()
        if item.get("replacement") is not None
    }
    missing_replacements = replacements - identities
    if missing_replacements:
        raise RegistryError(f"replacement identities missing: {sorted(missing_replacements)}")

    return {
        "contracts": len(identities),
        "claims": claim_count,
        "repositories": len(repository_heads),
    }


def main() -> int:
    try:
        summary = validate_registry()
    except RegistryError as exc:
        print(f"contract-consumer-registry: FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "valid", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
