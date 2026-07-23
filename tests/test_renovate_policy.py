from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "fleet" / "renovate_policy.py"
SPEC = importlib.util.spec_from_file_location("renovate_policy", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
renovate_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renovate_policy)


def _inputs():
    fleet = renovate_policy._load_yaml(ROOT / "fleet/repos.yml", label="fleet")
    policy = renovate_policy._load_yaml(
        ROOT / "automation/renovate/dependency-updates.v1.yml", label="policy"
    )
    preset = renovate_policy._load_json(
        ROOT / "automation/renovate/default.json", label="preset"
    )
    return fleet, policy, preset


def test_current_policy_preset_baseline_and_projection_are_valid() -> None:
    projection, summary = renovate_policy.validate_all()
    assert summary == {"active_fleet_count": 18, "explicit_rollout_count": 6}
    assert projection["expected_hosted_app_repositories"] == []
    assert projection["prepared_repositories"] == [
        "heimgewebe/hausKI",
        "heimgewebe/hausKI-audio",
        "heimgewebe/metarepo",
        "heimgewebe/mitschreiber",
        "heimgewebe/repoground",
        "heimgewebe/weltgewebe",
    ]
    committed = json.loads(
        (ROOT / "automation/renovate/expected-scope.v1.json").read_text(encoding="utf-8")
    )
    assert committed == projection


def test_archived_or_non_fleet_repository_is_rejected() -> None:
    fleet, policy, _ = _inputs()
    mutated = copy.deepcopy(policy)
    mutated["rollout"]["waves"][0]["repositories"][0]["name"] = "heimlern"
    with pytest.raises(renovate_policy.PolicyError, match="not active Fleet scope"):
        renovate_policy.validate_policy(
            mutated,
            active_fleet=renovate_policy.active_fleet_repositories(fleet),
        )


def test_repository_cannot_appear_in_multiple_waves() -> None:
    fleet, policy, _ = _inputs()
    mutated = copy.deepcopy(policy)
    mutated["rollout"]["waves"][1]["repositories"].append(
        {
            "name": "mitschreiber",
            "dependabot_version_updates": "none",
            "renovate_version_updates": "prepared",
        }
    )
    with pytest.raises(renovate_policy.PolicyError, match="more than one wave"):
        renovate_policy.validate_policy(
            mutated,
            active_fleet=renovate_policy.active_fleet_repositories(fleet),
        )


def test_two_active_version_update_producers_fail_closed() -> None:
    fleet, policy, _ = _inputs()
    mutated = copy.deepcopy(policy)
    repo = mutated["rollout"]["waves"][1]["repositories"][0]
    repo["dependabot_version_updates"] = "enabled"
    repo["renovate_version_updates"] = "enabled"
    with pytest.raises(renovate_policy.PolicyError, match="duplicate active"):
        renovate_policy.validate_policy(
            mutated,
            active_fleet=renovate_policy.active_fleet_repositories(fleet),
        )


def test_shared_preset_groups_only_github_actions_non_major_updates() -> None:
    _, _, preset = _inputs()
    assert [rule["matchManagers"] for rule in preset["packageRules"]] == [["github-actions"]]
    assert preset["packageRules"][0]["matchUpdateTypes"] == ["minor", "patch"]


def test_preset_cannot_enable_automerge() -> None:
    _, _, preset = _inputs()
    mutated = copy.deepcopy(preset)
    mutated["automerge"] = True
    with pytest.raises(renovate_policy.PolicyError, match="automerge=false"):
        renovate_policy.validate_preset(mutated)


def test_major_updates_cannot_be_added_to_grouped_rule() -> None:
    _, _, preset = _inputs()
    mutated = copy.deepcopy(preset)
    mutated["packageRules"][0]["matchUpdateTypes"].append("major")
    with pytest.raises(renovate_policy.PolicyError, match="major updates must remain isolated"):
        renovate_policy.validate_preset(mutated)


def test_observed_hosted_app_scope_must_match_enabled_policy_scope() -> None:
    projection, _ = renovate_policy.validate_all()
    renovate_policy.compare_observed_app_scope(projection, [])
    with pytest.raises(renovate_policy.PolicyError, match="differs"):
        renovate_policy.compare_observed_app_scope(
            projection,
            ["heimgewebe/mitschreiber"],
        )


def test_complete_fleet_copy_is_rejected_as_second_membership_list() -> None:
    fleet, policy, _ = _inputs()
    active = renovate_policy.active_fleet_repositories(fleet)
    mutated = copy.deepcopy(policy)
    explicit = {
        entry["name"]
        for wave in mutated["rollout"]["waves"]
        for entry in wave["repositories"]
    }
    mutated["rollout"]["waves"][0]["repositories"].extend(
        {
            "name": name,
            "dependabot_version_updates": "none",
            "renovate_version_updates": "disabled",
        }
        for name in sorted(active - explicit)
    )
    with pytest.raises(renovate_policy.PolicyError, match="complete active Fleet"):
        renovate_policy.validate_policy(mutated, active_fleet=active)
