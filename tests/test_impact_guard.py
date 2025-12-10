from pathlib import Path

from metarepo_tools.impact_guard import ContractMeta, build_mermaid


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
