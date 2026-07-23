#!/usr/bin/env python3
"""Validate and project the Fleet-bound Renovate V1 rollout policy.

The policy is operational metadata only. Fleet membership remains authoritative
in fleet/repos.yml. This tool deliberately produces a bounded Renovate scope
projection instead of a second complete Fleet registry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FLEET = ROOT / "fleet" / "repos.yml"
DEFAULT_POLICY = ROOT / "automation" / "renovate" / "dependency-updates.v1.yml"
DEFAULT_PRESET = ROOT / "automation" / "renovate" / "default.json"
DEFAULT_BASELINE = ROOT / "automation" / "renovate" / "baseline-2026-06-23_2026-07-23.json"
DEFAULT_SCOPE = ROOT / "automation" / "renovate" / "expected-scope.v1.json"

EXPECTED_BASELINE_WINDOW = {"start": "2026-06-23", "end": "2026-07-23"}
EXPECTED_BASELINE_TOTALS = {"total": 51, "merged": 40, "closed_unmerged": 11, "open": 0}
EXPECTED_BASELINE_REPOSITORIES = {
    "hausKI": {"total": 11, "merged": 10, "closed_unmerged": 1, "open": 0},
    "hausKI-audio": {"total": 10, "merged": 9, "closed_unmerged": 1, "open": 0},
    "metarepo": {"total": 5, "merged": 3, "closed_unmerged": 2, "open": 0},
    "repoground": {"total": 6, "merged": 1, "closed_unmerged": 5, "open": 0},
    "weltgewebe": {"total": 19, "merged": 17, "closed_unmerged": 2, "open": 0},
}
EXPECTED_CUTOVER_SEQUENCE = [
    "prove-renovate-coverage",
    "disable-overlapping-dependabot-version-updates",
    "verify-single-version-update-producer",
]
DEPENDABOT_STATES = {"enabled", "disabled", "none"}
RENOVATE_STATES = {"enabled", "prepared", "disabled"}
ALLOWED_SELECTOR = "remaining-eligible-active-fleet"


class PolicyError(ValueError):
    """Raised when Fleet-bound Renovate policy data is unsafe or inconsistent."""


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except FileNotFoundError as exc:
        raise PolicyError(f"{label} not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise PolicyError(f"{label} is not valid unique-key YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must have a mapping root")
    return value


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PolicyError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must have an object root")
    return value


def _exact_keys(
    value: dict[str, Any],
    *,
    allowed: set[str],
    required: set[str],
    label: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise PolicyError(f"{label} contains unsupported fields: {', '.join(unknown)}")
    if missing:
        raise PolicyError(f"{label} is missing required fields: {', '.join(missing)}")


def _entry_name(entry: Any, *, label: str) -> str:
    if isinstance(entry, str) and entry.strip():
        return entry.strip()
    if isinstance(entry, dict):
        name = entry.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    raise PolicyError(f"{label} must contain a non-empty repository name")


def active_fleet_repositories(fleet: dict[str, Any]) -> set[str]:
    repos = fleet.get("repos")
    if not isinstance(repos, list):
        raise PolicyError("fleet/repos.yml must contain a repos list")
    static = fleet.get("static", {}) or {}
    if not isinstance(static, dict):
        raise PolicyError("fleet/repos.yml static must be a mapping")
    include = static.get("include", []) or []
    if not isinstance(include, list):
        raise PolicyError("fleet/repos.yml static.include must be a list")

    active: set[str] = set()
    seen: set[str] = set()
    for label, entries in (("repos", repos), ("static.include", include)):
        for index, entry in enumerate(entries):
            name = _entry_name(entry, label=f"{label}[{index}]")
            if name in seen:
                raise PolicyError(f"repository occurs more than once in Fleet scope: {name}")
            seen.add(name)
            if isinstance(entry, dict):
                fleet_flag = entry.get("fleet", True)
                if not isinstance(fleet_flag, bool):
                    raise PolicyError(f"{label}[{index}].fleet must be boolean")
                status = entry.get("status")
                if status is not None and (not isinstance(status, str) or not status.strip()):
                    raise PolicyError(f"{label}[{index}].status must be a non-empty string")
                if fleet_flag is False or status == "archived-reference":
                    continue
            active.add(name)
    if not active:
        raise PolicyError("Fleet contains no active projectable repositories")
    return active


def validate_preset(preset: dict[str, Any]) -> None:
    _exact_keys(
        preset,
        allowed={
            "$schema",
            "description",
            "extends",
            "automerge",
            "dependencyDashboard",
            "prConcurrentLimit",
            "branchConcurrentLimit",
            "prHourlyLimit",
            "separateMajorMinor",
            "labels",
            "packageRules",
        },
        required={
            "$schema",
            "extends",
            "automerge",
            "prConcurrentLimit",
            "branchConcurrentLimit",
            "prHourlyLimit",
            "separateMajorMinor",
            "packageRules",
        },
        label="Renovate preset",
    )
    extends = preset["extends"]
    if not isinstance(extends, list) or "config:recommended" not in extends:
        raise PolicyError("Renovate preset must extend config:recommended")
    if preset["automerge"] is not False:
        raise PolicyError("Renovate preset must set automerge=false")
    if preset["separateMajorMinor"] is not True:
        raise PolicyError("Renovate preset must keep major updates separate")
    for field in ("prConcurrentLimit", "branchConcurrentLimit", "prHourlyLimit"):
        value = preset[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > 2:
            raise PolicyError(f"Renovate preset {field} must be an integer between 1 and 2")

    rules = preset["packageRules"]
    if not isinstance(rules, list) or not rules:
        raise PolicyError("Renovate preset packageRules must be a non-empty list")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise PolicyError(f"packageRules[{index}] must be an object")
        _exact_keys(
            rule,
            allowed={"description", "matchManagers", "matchUpdateTypes", "groupName"},
            required={"matchManagers", "matchUpdateTypes", "groupName"},
            label=f"packageRules[{index}]",
        )
        managers = rule["matchManagers"]
        update_types = rule["matchUpdateTypes"]
        group_name = rule["groupName"]
        if not isinstance(managers, list) or not managers or not all(
            isinstance(item, str) and item.strip() for item in managers
        ):
            raise PolicyError(f"packageRules[{index}].matchManagers must be non-empty strings")
        if not isinstance(update_types, list) or not update_types:
            raise PolicyError(f"packageRules[{index}].matchUpdateTypes must be non-empty")
        if set(update_types) - {"minor", "patch"}:
            raise PolicyError(
                f"packageRules[{index}] groups unsupported update types; major updates must remain isolated"
            )
        if not isinstance(group_name, str) or not group_name.strip():
            raise PolicyError(f"packageRules[{index}].groupName must be non-empty")


def validate_baseline(baseline: dict[str, Any]) -> None:
    _exact_keys(
        baseline,
        allowed={"schema_version", "kind", "window", "source", "repositories", "totals", "nonclaims"},
        required={"schema_version", "kind", "window", "source", "repositories", "totals", "nonclaims"},
        label="Dependabot baseline",
    )
    if baseline["schema_version"] != 1 or baseline["kind"] != "dependabot-pr-baseline":
        raise PolicyError("Dependabot baseline identity is unsupported")
    if baseline["window"] != EXPECTED_BASELINE_WINDOW:
        raise PolicyError("Dependabot baseline window must remain the reviewed 2026-06-23..2026-07-23 window")
    if baseline["totals"] != EXPECTED_BASELINE_TOTALS:
        raise PolicyError("Dependabot baseline totals differ from reviewed evidence")
    if baseline["repositories"] != EXPECTED_BASELINE_REPOSITORIES:
        raise PolicyError("Dependabot per-repository baseline differs from reviewed evidence")
    calculated = {key: 0 for key in EXPECTED_BASELINE_TOTALS}
    for values in baseline["repositories"].values():
        if not isinstance(values, dict):
            raise PolicyError("Dependabot repository baseline entries must be objects")
        for key in calculated:
            value = values.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise PolicyError(f"Dependabot repository baseline {key} must be a non-negative integer")
            calculated[key] += value
    if calculated != baseline["totals"]:
        raise PolicyError("Dependabot baseline totals do not equal per-repository sums")


def validate_policy(policy: dict[str, Any], *, active_fleet: set[str]) -> list[dict[str, Any]]:
    _exact_keys(
        policy,
        allowed={
            "schema_version",
            "kind",
            "fleet_source",
            "github_owner",
            "security_updates",
            "version_update_defaults",
            "cutover_sequence",
            "rollout",
        },
        required={
            "schema_version",
            "kind",
            "fleet_source",
            "github_owner",
            "security_updates",
            "version_update_defaults",
            "cutover_sequence",
            "rollout",
        },
        label="Renovate Fleet policy",
    )
    if policy["schema_version"] != 1 or policy["kind"] != "renovate-fleet-policy":
        raise PolicyError("Renovate Fleet policy identity is unsupported")
    if policy["fleet_source"] != "fleet/repos.yml":
        raise PolicyError("Renovate Fleet policy must bind membership to fleet/repos.yml")
    owner = policy["github_owner"]
    if not isinstance(owner, str) or not owner.strip():
        raise PolicyError("github_owner must be a non-empty string")

    security = policy["security_updates"]
    if not isinstance(security, dict):
        raise PolicyError("security_updates must be a mapping")
    _exact_keys(
        security,
        allowed={"provider", "version_update_cutover_changes_security_updates"},
        required={"provider", "version_update_cutover_changes_security_updates"},
        label="security_updates",
    )
    if security["provider"] != "dependabot":
        raise PolicyError("Renovate V1 keeps Dependabot as the declared security-update provider")
    if security["version_update_cutover_changes_security_updates"] is not False:
        raise PolicyError("version-update cutover may not claim to change the security-update path")

    defaults = policy["version_update_defaults"]
    if not isinstance(defaults, dict):
        raise PolicyError("version_update_defaults must be a mapping")
    _exact_keys(
        defaults,
        allowed={
            "provider",
            "automerge",
            "duplicate_producer_policy",
            "runtime_mode",
            "credential_source",
            "scope_selector",
            "all_repositories_allowed",
        },
        required={
            "provider",
            "automerge",
            "duplicate_producer_policy",
            "runtime_mode",
            "credential_source",
            "scope_selector",
            "all_repositories_allowed",
        },
        label="version_update_defaults",
    )
    expected_defaults = {
        "provider": "renovate",
        "automerge": False,
        "duplicate_producer_policy": "fail-closed",
        "runtime_mode": "self-hosted-heim-pc",
        "credential_source": "gh-auth-token-transient",
        "scope_selector": "active-fleet",
        "all_repositories_allowed": False,
    }
    if defaults != expected_defaults:
        raise PolicyError("version_update_defaults do not match the reviewed Renovate V1 safety contract")
    if policy["cutover_sequence"] != EXPECTED_CUTOVER_SEQUENCE:
        raise PolicyError("cutover_sequence must prove coverage, disable overlap, then verify one producer")

    rollout = policy["rollout"]
    if not isinstance(rollout, dict):
        raise PolicyError("rollout must be a mapping")
    _exact_keys(rollout, allowed={"waves"}, required={"waves"}, label="rollout")
    waves = rollout["waves"]
    if not isinstance(waves, list) or not waves:
        raise PolicyError("rollout.waves must be a non-empty list")

    seen_ids: set[str] = set()
    seen_orders: set[int] = set()
    seen_repositories: set[str] = set()
    normalized: list[dict[str, Any]] = []
    selector_count = 0
    for index, wave in enumerate(waves):
        if not isinstance(wave, dict):
            raise PolicyError(f"rollout.waves[{index}] must be a mapping")
        _exact_keys(
            wave,
            allowed={"id", "order", "purpose", "repositories", "selector"},
            required={"id", "order", "purpose", "repositories"},
            label=f"rollout.waves[{index}]",
        )
        wave_id = wave["id"]
        order = wave["order"]
        purpose = wave["purpose"]
        if not isinstance(wave_id, str) or not wave_id.strip() or wave_id in seen_ids:
            raise PolicyError(f"rollout.waves[{index}].id must be unique and non-empty")
        if not isinstance(order, int) or isinstance(order, bool) or order < 1 or order in seen_orders:
            raise PolicyError(f"rollout.waves[{index}].order must be a unique positive integer")
        if not isinstance(purpose, str) or not purpose.strip():
            raise PolicyError(f"rollout.waves[{index}].purpose must be non-empty")
        seen_ids.add(wave_id)
        seen_orders.add(order)

        selector = wave.get("selector")
        repositories = wave["repositories"]
        if not isinstance(repositories, list):
            raise PolicyError(f"rollout.waves[{index}].repositories must be a list")
        if selector is not None:
            selector_count += 1
            if selector != ALLOWED_SELECTOR:
                raise PolicyError(f"rollout.waves[{index}].selector is unsupported")
            if repositories:
                raise PolicyError("selector-based Fleet expansion may not duplicate an explicit repository list")
        entries: list[dict[str, str]] = []
        for repo_index, repo in enumerate(repositories):
            if not isinstance(repo, dict):
                raise PolicyError(f"rollout.waves[{index}].repositories[{repo_index}] must be a mapping")
            _exact_keys(
                repo,
                allowed={"name", "dependabot_version_updates", "renovate_version_updates"},
                required={"name", "dependabot_version_updates", "renovate_version_updates"},
                label=f"rollout.waves[{index}].repositories[{repo_index}]",
            )
            name = repo["name"]
            dependabot = repo["dependabot_version_updates"]
            renovate = repo["renovate_version_updates"]
            if not isinstance(name, str) or not name.strip():
                raise PolicyError("rollout repository name must be non-empty")
            name = name.strip()
            if name not in active_fleet:
                raise PolicyError(f"Renovate rollout repository is not active Fleet scope: {name}")
            if name in seen_repositories:
                raise PolicyError(f"Renovate rollout repository occurs in more than one wave: {name}")
            if dependabot not in DEPENDABOT_STATES:
                raise PolicyError(f"unsupported Dependabot version-update state for {name}: {dependabot}")
            if renovate not in RENOVATE_STATES:
                raise PolicyError(f"unsupported Renovate version-update state for {name}: {renovate}")
            if dependabot == "enabled" and renovate == "enabled":
                raise PolicyError(f"duplicate active version-update producers for {name}")
            seen_repositories.add(name)
            entries.append(
                {
                    "name": name,
                    "dependabot_version_updates": dependabot,
                    "renovate_version_updates": renovate,
                }
            )
        normalized.append(
            {
                "id": wave_id,
                "order": order,
                "purpose": purpose.strip(),
                "selector": selector,
                "repositories": entries,
            }
        )

    if selector_count != 1:
        raise PolicyError("Renovate V1 must have exactly one deferred remaining-Fleet selector")
    if seen_repositories == active_fleet:
        raise PolicyError("Renovate policy may not duplicate the complete active Fleet membership list")
    return sorted(normalized, key=lambda item: item["order"])


def build_scope_projection(
    *,
    policy: dict[str, Any],
    waves: list[dict[str, Any]],
    active_fleet: set[str],
    fleet_path: Path,
    policy_path: Path,
) -> dict[str, Any]:
    owner = policy["github_owner"].strip()
    prepared: list[str] = []
    enabled: list[str] = []
    ownership: list[dict[str, Any]] = []
    projected_waves: list[dict[str, Any]] = []
    selectors: list[str] = []
    explicit_names = {
        repo["name"]
        for wave in waves
        for repo in wave["repositories"]
    }

    def add_repo(name: str, dependabot_state: str, renovate_state: str) -> None:
        full_name = f"{owner}/{name}"
        if renovate_state == "prepared":
            prepared.append(full_name)
        elif renovate_state == "enabled":
            enabled.append(full_name)
        ownership.append(
            {
                "repository": full_name,
                "dependabot_version_updates": dependabot_state,
                "renovate_version_updates": renovate_state,
            }
        )

    for wave in waves:
        repo_names: list[str] = []
        for repo in wave["repositories"]:
            name = repo["name"]
            repo_names.append(name)
            add_repo(
                name,
                repo["dependabot_version_updates"],
                repo["renovate_version_updates"],
            )
        if wave["selector"] is not None:
            selectors.append(wave["selector"])
            derived = sorted(active_fleet - explicit_names)
            repo_names.extend(derived)
            for name in derived:
                add_repo(name, "none", "enabled")
        projected_waves.append(
            {
                "id": wave["id"],
                "order": wave["order"],
                "repositories": repo_names,
                "selector": wave["selector"],
            }
        )

    enabled = sorted(set(enabled))
    if set(enabled) != {f"{owner}/{name}" for name in active_fleet}:
        raise PolicyError("direct-cutover projection must enable Renovate for the complete active Fleet")

    return {
        "schema_version": 1,
        "kind": "renovate-fleet-scope-projection",
        "runtime_mode": policy["version_update_defaults"]["runtime_mode"],
        "credential_source": policy["version_update_defaults"]["credential_source"],
        "sources": {
            "fleet": {"path": "fleet/repos.yml", "sha256": _sha256(fleet_path)},
            "policy": {
                "path": "automation/renovate/dependency-updates.v1.yml",
                "sha256": _sha256(policy_path),
            },
        },
        "expected_renovate_repositories": enabled,
        "expected_hosted_app_repositories": [],
        "prepared_repositories": sorted(set(prepared)),
        "version_update_ownership": sorted(ownership, key=lambda item: item["repository"]),
        "waves": projected_waves,
        "deferred_selectors": selectors,
        "nonclaims": [
            "This projection is not Fleet membership truth.",
            "The self-hosted runtime target list is derived from fleet/repos.yml and this policy.",
            "An empty expected hosted-app scope is not proof that no external app installation exists.",
            "This projection grants no merge, queue, claim, deployment or task-verification authority.",
        ],
    }


def render_projection(projection: dict[str, Any]) -> str:
    return json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def compare_observed_app_scope(projection: dict[str, Any], observed: Any) -> None:
    if isinstance(observed, dict):
        _exact_keys(observed, allowed={"repositories"}, required={"repositories"}, label="observed app scope")
        observed = observed["repositories"]
    if not isinstance(observed, list) or not all(isinstance(item, str) and item.strip() for item in observed):
        raise PolicyError("observed app scope must be a list of repository names")
    normalized = sorted(item.strip() for item in observed)
    if len(normalized) != len(set(normalized)):
        raise PolicyError("observed app scope contains duplicate repositories")
    expected = projection["expected_hosted_app_repositories"]
    if normalized != expected:
        raise PolicyError(
            "observed hosted Renovate app scope differs from Git-authored expected scope: "
            f"expected={expected} observed={normalized}"
        )


def validate_all(
    *,
    fleet_path: Path = DEFAULT_FLEET,
    policy_path: Path = DEFAULT_POLICY,
    preset_path: Path = DEFAULT_PRESET,
    baseline_path: Path = DEFAULT_BASELINE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fleet = _load_yaml(fleet_path, label="Fleet membership")
    policy = _load_yaml(policy_path, label="Renovate Fleet policy")
    preset = _load_json(preset_path, label="Renovate shared preset")
    baseline = _load_json(baseline_path, label="Dependabot baseline")
    active = active_fleet_repositories(fleet)
    waves = validate_policy(policy, active_fleet=active)
    validate_preset(preset)
    validate_baseline(baseline)
    projection = build_scope_projection(
        policy=policy,
        waves=waves,
        active_fleet=active,
        fleet_path=fleet_path,
        policy_path=policy_path,
    )
    return projection, {
        "active_fleet_count": len(active),
        "explicit_rollout_count": sum(len(w["repositories"]) for w in waves),
    }


def _read_observed_scope(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyError(f"observed app scope not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PolicyError(f"observed app scope is not valid JSON: {exc}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate", help="write the deterministic Renovate scope projection")
    generate.add_argument("--output", type=Path, default=DEFAULT_SCOPE)
    check = sub.add_parser(
        "check", help="validate policy/preset/baseline and committed scope projection"
    )
    check.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    check.add_argument("--observed-app-scope", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    projection, summary = validate_all()
    expected = render_projection(projection)
    if args.command == "generate":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
        print(f"wrote Renovate scope projection: {args.output}")
        return 0

    try:
        current = args.scope.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PolicyError(f"Renovate scope projection missing: {args.scope}") from exc
    if current != expected:
        raise PolicyError("Renovate scope projection is stale; run renovate_policy.py generate")
    if args.observed_app_scope is not None:
        compare_observed_app_scope(projection, _read_observed_scope(args.observed_app_scope))
    print(
        json.dumps(
            {
                "status": "ok",
                "active_fleet_count": summary["active_fleet_count"],
                "explicit_rollout_count": summary["explicit_rollout_count"],
                "expected_renovate_repositories": projection[
                    "expected_renovate_repositories"
                ],
                "expected_hosted_app_repositories": projection[
                    "expected_hosted_app_repositories"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
