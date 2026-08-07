import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "repository-verification.v2.schema.json"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_contract_has_metarepo_authority_and_current_consumers() -> None:
    schema = _schema()
    assert schema["x-producers"] == ["metarepo"]
    assert {"wgx", "github-actions", "grabowski"} <= set(schema["x-consumers"])
    Draft202012Validator.check_schema(schema)


def test_versioned_example_matches_contract() -> None:
    payload = json.loads(
        (ROOT / "contracts" / "examples" / "repository-verification.v2.example.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(_schema()).validate(payload)


def test_active_and_template_profiles_match_contract() -> None:
    validator = Draft202012Validator(_schema())
    for path in (ROOT / ".wgx" / "profile.yml", ROOT / "templates" / ".wgx" / "profile.yml"):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        validator.validate(payload)
        tasks = payload["wgx"]["tasks"]
        assert "guard" in tasks
        assert "smoke" in tasks


def test_metarepo_guard_is_deterministic_and_repo_owned() -> None:
    payload = yaml.safe_load((ROOT / ".wgx" / "profile.yml").read_text(encoding="utf-8"))
    guard = payload["wgx"]["tasks"]["guard"]
    assert "scripts/ci/check_wgx_reusable_callers.py" in guard
    assert "scripts/check-contracts-index.sh" in guard
    assert "git diff --check" in guard
    assert "command -v" not in guard
    assert "yamllint ." not in guard
    assert ".repo-verification-runner" not in guard


def test_reusable_workflow_is_policy_owner_not_wgx_workflow_proxy() -> None:
    workflow = (ROOT / ".github" / "workflows" / "reusable-repo-verify.yml").read_text(
        encoding="utf-8"
    )
    assert "repository: heimgewebe/wgx" in workflow
    assert "heimgewebe/wgx/.github/workflows/" not in workflow


def test_reusable_workflow_passes_read_token_to_repository_verifier() -> None:
    workflow = (ROOT / ".github" / "workflows" / "reusable-repo-verify.yml").read_text(
        encoding="utf-8"
    )
    assert "GITHUB_TOKEN: ${{ github.token }}" in workflow
    assert "guard|smoke" in workflow
    assert "quick|full" in workflow
