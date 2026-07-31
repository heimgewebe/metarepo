from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "reusable-ci.yml"
LOCAL_PIN_CONDITION = (
    "${{ hashFiles('scripts/tools/just-pin.sh') != '' "
    "&& hashFiles('scripts/lib/semver.sh') != '' "
    "&& hashFiles('scripts/lib/installer.bash') != '' "
    "&& hashFiles('toolchain.versions.yml') != '' }}"
)
MISSING_PIN_STACK = (
    "!(hashFiles('scripts/tools/just-pin.sh') != '' "
    "&& hashFiles('scripts/lib/semver.sh') != '' "
    "&& hashFiles('scripts/lib/installer.bash') != '' "
    "&& hashFiles('toolchain.versions.yml') != '')"
)
AGENT_FALLBACK_CONDITION = f"${{{{ {MISSING_PIN_STACK} && env.AGENT_MODE != '' }}}}"
NETWORK_FALLBACK_CONDITION = f"${{{{ {MISSING_PIN_STACK} && env.AGENT_MODE == '' }}}}"
SETUP_JUST_SHA = "53165ef7e734c5c07cb06b3c8e7b647c5aa16db3"


def _document() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps(document: dict) -> dict[str, dict]:
    steps = document["jobs"]["reusable-ci"]["steps"]
    return {step["name"]: step for step in steps if "name" in step}


def _portability_errors(document: dict) -> list[str]:
    errors: list[str] = []
    inputs = document["on"]["workflow_call"]["inputs"]
    steps = _steps(document)
    local = steps.get("Setup Just from caller repository pin")
    agent = steps.get("Verify preinstalled Just in Agent Mode")
    fallback = steps.get("Setup Just fallback")

    if inputs.get("just_version", {}).get("default") != "1.43.0":
        errors.append("missing exact default Just version")
    if local is None or local.get("if") != LOCAL_PIN_CONDITION:
        errors.append("repository-local installer is not presence-guarded")
    if agent is None or agent.get("if") != AGENT_FALLBACK_CONDITION:
        errors.append("Agent Mode lacks a no-download fallback")
    if fallback is None or fallback.get("if") != NETWORK_FALLBACK_CONDITION:
        errors.append("callers without installer lack a network fallback")
    expected_action = f"extractions/setup-just@{SETUP_JUST_SHA}"
    if fallback is None or fallback.get("uses") != expected_action:
        errors.append("fallback action is not revision-pinned")
    if fallback is None or fallback.get("with", {}).get("just-version") != "${{ inputs.just_version }}":
        errors.append("fallback does not consume the exact version input")
    return errors


def test_reusable_ci_is_caller_independent_and_revision_pinned() -> None:
    assert _portability_errors(_document()) == []


def test_unconditional_caller_local_installer_regression_is_rejected() -> None:
    document = deepcopy(_document())
    steps = document["jobs"]["reusable-ci"]["steps"]
    steps[:] = [
        step
        for step in steps
        if step.get("name")
        not in {"Verify preinstalled Just in Agent Mode", "Setup Just fallback"}
    ]
    local = next(
        step
        for step in steps
        if step.get("name") == "Setup Just from caller repository pin"
    )
    local.pop("if")

    errors = _portability_errors(document)
    assert "repository-local installer is not presence-guarded" in errors
    assert "callers without installer lack a network fallback" in errors


def test_partial_repository_pin_stack_uses_fallback() -> None:
    document = deepcopy(_document())
    local = _steps(document)["Setup Just from caller repository pin"]
    local["if"] = "${{ hashFiles('scripts/tools/just-pin.sh') != '' }}"

    errors = _portability_errors(document)
    assert "repository-local installer is not presence-guarded" in errors
