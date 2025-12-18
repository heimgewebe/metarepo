from pathlib import Path

from metarepo_tools.impact_guard import ContractMeta, build_mermaid, load_manifest


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
