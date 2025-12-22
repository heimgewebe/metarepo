from pathlib import Path

from metarepo_tools.impact_guard import (
    ContractMeta,
    build_mermaid,
    build_report,
    compute_dependents,
    load_manifest,
)


def test_load_manifest_handles_empty_files(tmp_path):
    manifest_path = tmp_path / "repos.yml"
    manifest_path.write_text("")

    manifest = load_manifest(manifest_path)

    assert manifest == {}


def test_load_manifest_ignores_invalid_repo_entries(tmp_path):
    manifest_path = tmp_path / "repos.yml"
    manifest_path.write_text(
        """
        repos:
          - name: alpha
            domain: core
          - 42"""
    )

    manifest = load_manifest(manifest_path)

    assert manifest == {"alpha": {"name": "alpha", "domain": "core"}}


def test_compute_dependents_handles_string_and_iterable_entries():
    manifest = {
        "repo-a": {"depends_on": "core"},
        "repo-b": {"depends_on": ["core", "shared"]},
        "repo-c": {"depends_on": ("shared",)},
    }

    warnings: list[str] = []
    dependents = compute_dependents(manifest, warnings=warnings)

    assert dependents == {
        "core": ["repo-a", "repo-b"],
        "shared": ["repo-b", "repo-c"],
    }
    assert warnings == []


def test_build_mermaid_omits_leading_colon_when_only_scope_present():
    contracts = {
        "contracts/demo.schema.json": ContractMeta(
            path=Path("contracts/demo.schema.json"),
            contract_id="demo",
            title="Demo contract",
            producers=["demo"],
            consumers=[],
        )
    }
    manifest = {"demo": {"scope": "ops"}}

    graph = build_mermaid(contracts, manifest)

    assert 'repo_demo["demo<br/>ops"]' in graph.splitlines()
    assert '<br/>:ops' not in graph


def test_build_report_normalises_depends_on_entries():
    contract = ContractMeta(
        path=Path("contracts/demo.schema.json"),
        contract_id="demo",
        title="Demo contract",
        producers=["repo-a"],
        consumers=["repo-b"],
    )
    contracts = {"contracts/demo.schema.json": contract}
    manifest = {
        "repo-a": {"domain": "core", "depends_on": "shared"},
        "repo-b": {"depends_on": ("shared",)},
        "shared": {},
    }

    summary = build_report(["contracts/demo.schema.json"], contracts, manifest)

    repo_a = summary["impacted_repos"]["repo-a"]
    repo_b = summary["impacted_repos"]["repo-b"]
    assert repo_a["depends_on"] == ["shared"]
    assert repo_b["depends_on"] == ["shared"]


def test_build_report_emits_warnings_for_invalid_depends_on_entries():
    contract = ContractMeta(
        path=Path("contracts/demo.schema.json"),
        contract_id="demo",
        title="Demo contract",
        producers=["repo-a"],
        consumers=["repo-b"],
    )
    contracts = {"contracts/demo.schema.json": contract}
    manifest = {
        "repo-a": {"depends_on": {"core": True}},
        "repo-b": {"depends_on": [42, None, "core"]},
    }

    summary = build_report(["contracts/demo.schema.json"], contracts, manifest)

    assert summary["impacted_repos"]["repo-a"]["depends_on"] == []
    assert summary["impacted_repos"]["repo-b"]["depends_on"] == ["core"]
    assert any("manifest.repo-a" in msg for msg in summary["warnings"])
    assert any("manifest.repo-b" in msg and "ignored" in msg for msg in summary["warnings"])


def test_build_report_deduplicates_warnings_and_stabilises_sets():
    contract = ContractMeta(
        path=Path("contracts/demo.schema.json"),
        contract_id="demo",
        title="Demo contract",
        producers=["repo-a"],
        consumers=["repo-b"],
    )
    contracts = {"contracts/demo.schema.json": contract}
    manifest = {
        "repo-a": {"depends_on": {"core": True}},
        "repo-b": {"depends_on": {"core", "shared"}},
    }

    summary = build_report(["contracts/demo.schema.json"], contracts, manifest)

    # repo-a warning should only appear once even though depends_on is read twice
    warn_msgs = [msg for msg in summary["warnings"] if "manifest.repo-a" in msg]
    assert len(warn_msgs) == 1
    # set input yields deterministic ordering
    assert summary["impacted_repos"]["repo-b"]["depends_on"] == ["core", "shared"]
