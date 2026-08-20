from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "contracts" / "package.json"
PACKAGE_LOCK = ROOT / "contracts" / "package-lock.json"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate-contracts.sh"
AJV_RUNNER = ROOT / "scripts" / "contracts" / "ajv_validate.cjs"

EXPECTED_DEPENDENCIES = {
    "ajv": "8.20.0",
    "ajv-formats": "3.0.1",
}
FORBIDDEN_PACKAGES = {
    "ajv-cli",
    "brace-expansion",
    "fast-json-patch",
    "glob",
    "inflight",
    "json-schema-migrate",
    "minimatch",
}


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _locked_package_names(lock: dict[str, object]) -> set[str]:
    packages = lock.get("packages")
    assert isinstance(packages, dict)

    names: set[str] = set()
    marker = "node_modules/"
    for package_path in packages:
        if not isinstance(package_path, str) or marker not in package_path:
            continue
        names.add(package_path.rsplit(marker, maxsplit=1)[1])
    return names


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _contract_validator_fixture(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    (repo / "scripts/contracts").mkdir(parents=True)
    (repo / "contracts/examples").mkdir(parents=True)

    validator = repo / "scripts/validate-contracts.sh"
    validator.write_text(VALIDATE_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    validator.chmod(0o755)
    (repo / "scripts/contracts/ajv_validate.cjs").write_text("// test stub\n", encoding="utf-8")
    (repo / "scripts/check-contract-json.py").write_text("# test stub\n", encoding="utf-8")
    (repo / "scripts/contracts/validate_consumers.py").write_text("# test stub\n", encoding="utf-8")
    (repo / "contracts/package.json").write_text("{}\n", encoding="utf-8")
    (repo / "contracts/package-lock.json").write_text("{}\n", encoding="utf-8")

    fake_bin = repo / "fake-bin"
    _write_executable(fake_bin / "npm", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(fake_bin / "python3", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(fake_bin / "uv", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(
        fake_bin / "node",
        """#!/usr/bin/env bash
if [[ "${1:-}" == "-p" ]]; then
  case "${3:-}" in
    *ajv-formats/package.json) printf '%s\\n' '3.0.1' ;;
    *) printf '%s\\n' '8.20.0' ;;
  esac
fi
exit 0
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
    return repo, env


def _write_schema(repo: Path, relative_path: str, schema_id: str) -> None:
    schema = repo / relative_path
    schema.parent.mkdir(parents=True, exist_ok=True)
    schema.write_text(json.dumps({"$id": schema_id, "type": "object"}) + "\n", encoding="utf-8")


def _run_contract_validator(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/validate-contracts.sh"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_contract_manifest_uses_direct_pinned_ajv_runtime() -> None:
    package = _load_json(PACKAGE_JSON)

    assert package["devDependencies"] == EXPECTED_DEPENDENCIES
    assert package["scripts"] == {"validate": "bash ../scripts/validate-contracts.sh"}


def test_contract_lock_excludes_legacy_cli_dependency_chain() -> None:
    lock = _load_json(PACKAGE_LOCK)
    root_package = lock["packages"][""]

    assert root_package["devDependencies"] == EXPECTED_DEPENDENCIES
    assert _locked_package_names(lock).isdisjoint(FORBIDDEN_PACKAGES)


def test_contract_orchestrator_invokes_lock_bound_direct_runner() -> None:
    script = VALIDATE_SCRIPT.read_text(encoding="utf-8")

    assert "ajv-cli" not in script
    assert "AJV_VERSION=8.20.0" in script
    assert "AJV_FORMATS_VERSION=3.0.1" in script
    assert 'AJV_RUNNER="$ROOT_DIR/scripts/contracts/ajv_validate.cjs"' in script
    assert 'AJV_PACKAGE_LOCK="$ROOT_DIR/contracts/package-lock.json"' in script
    assert "npm ci --prefix" in script
    assert "npm install --prefix" not in script
    assert 'node "$AJV_RUNNER"' in script


def test_contract_examples_fail_closed_on_ambiguous_schema_matches(tmp_path: Path) -> None:
    repo, env = _contract_validator_fixture(tmp_path)
    (repo / "contracts/examples/widget.example.json").write_text("{}\n", encoding="utf-8")
    _write_schema(repo, "contracts/alpha/widget.schema.json", "urn:test:alpha:widget")
    _write_schema(repo, "contracts/beta/widget.schema.json", "urn:test:beta:widget")

    completed = _run_contract_validator(repo, env)

    assert completed.returncode == 2
    assert "Ambiguous schema match for contracts/examples/widget.example.json" in completed.stdout
    assert "contracts/alpha/widget.schema.json" in completed.stdout
    assert "contracts/beta/widget.schema.json" in completed.stdout


def test_contract_examples_keep_unique_directory_disambiguation(tmp_path: Path) -> None:
    repo, env = _contract_validator_fixture(tmp_path)
    example = repo / "contracts/examples/alpha/widget.example.json"
    example.parent.mkdir(parents=True)
    example.write_text("{}\n", encoding="utf-8")
    _write_schema(repo, "contracts/alpha/widget.schema.json", "urn:test:alpha:widget")
    _write_schema(repo, "contracts/beta/widget.schema.json", "urn:test:beta:widget")

    completed = _run_contract_validator(repo, env)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Validate Example contracts/examples/alpha/widget.example.json" in completed.stdout
    assert "Ambiguous schema match" not in completed.stdout


def test_direct_ajv_runner_is_valid_javascript() -> None:
    completed = subprocess.run(
        ["node", "--check", str(AJV_RUNNER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr


def test_direct_ajv_runner_fails_closed_without_pinned_modules(tmp_path: Path) -> None:
    schema = tmp_path / "schema.json"
    schema.write_text('{"$schema":"https://json-schema.org/draft/2020-12/schema"}', encoding="utf-8")

    completed = subprocess.run(
        [
            "node",
            str(AJV_RUNNER),
            "compile",
            "--modules",
            str(tmp_path / "missing-node-modules"),
            "--schema",
            str(schema),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "unable to load pinned AJV modules" in completed.stderr