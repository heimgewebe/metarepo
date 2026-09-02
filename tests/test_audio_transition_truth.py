from __future__ import annotations

import json
from pathlib import Path

import yaml

from wgx import repo_config

ROOT = Path(__file__).resolve().parents[1]


def test_audio_is_canonical_fleet_member_and_donor_is_non_fleet() -> None:
    fleet = repo_config.load_config(ROOT / "fleet/repos.yml")
    active = repo_config.active_fleet_names(fleet)
    assert "audio" in active
    assert "hausKI-audio" not in active
    assert len(active) == 18
    donor = next(
        entry
        for entry in fleet["static"]["include"]
        if entry["name"] == "hausKI-audio"
    )
    assert donor["status"] == "historical-donor"
    assert donor["fleet"] is False


def test_audio_operational_metadata_is_fail_closed() -> None:
    metadata = yaml.safe_load(
        (ROOT / "fleet/repo-metadata.yml").read_text(encoding="utf-8")
    )["repositories"]["audio"]
    assert metadata["wgx"]["profile_expected"] is False
    assert metadata["integrity"]["enabled"] is False
    assert metadata["scope"] == "configuration-and-experiments"


def test_active_ai_context_and_historical_donor_context_are_separate() -> None:
    audio = yaml.safe_load(
        (ROOT / "ai-contexts/audio.ai-context.yml").read_text(encoding="utf-8")
    )
    donor = yaml.safe_load(
        (ROOT / "ai-contexts/hausKI-audio.ai-context.yml").read_text(encoding="utf-8")
    )
    assert audio["project"]["name"] == "audio"
    assert audio["heimgewebe"]["fleet"]["enabled"] is True
    assert audio["source_binding"]["commit"] == "9ddefba90679adaf20be2e7e152f4d4aea068e77"
    assert donor["project"]["role"] == "historical_donor"
    assert donor["heimgewebe"]["fleet"]["enabled"] is False
    assert donor["interfaces"]["produces"] == ["none (historical donor)"]


def test_historical_audio_events_contract_has_no_active_binding() -> None:
    schema = json.loads(
        (ROOT / "contracts/audio.events.schema.json").read_text(encoding="utf-8")
    )
    assert schema["x-lifecycle"] == "historical"
    assert schema["x-producers"] == []
    assert schema["x-consumers"] == []
    bindings = schema["x-historical-bindings"]
    assert bindings["producer"]["repository"] == "heimgewebe/hausKI-audio"
    assert bindings["producer"]["commit"] == "4f2b4bdbfaa6419725aba02acd71347ac1e9da02"
    assert bindings["canonical_audio_repository"]["assessment"] == "no producer binding observed"


def test_generated_consumers_use_audio_but_do_not_claim_integrity() -> None:
    fleet_txt = (ROOT / "fleet/repos.txt").read_text(encoding="utf-8").splitlines()
    assert "audio" in fleet_txt
    assert "hausKI-audio" not in fleet_txt
    sources = json.loads(
        (ROOT / "reports/integrity/sources.v1.json").read_text(encoding="utf-8")
    )["sources"]
    source_map = {entry["repo"]: entry for entry in sources}
    assert "heimgewebe/hausKI-audio" not in source_map
    assert source_map["heimgewebe/audio"]["enabled"] is False
    assert "heimgewebe/commonthing" in source_map


def test_human_views_are_source_bound_and_historical_views_are_marked() -> None:
    matrix = (ROOT / "docs/repo-matrix.md").read_text(encoding="utf-8")
    active_section = matrix.split("## Historische Spender", 1)[0]
    assert "Canonical source: fleet/repos.yml" in matrix
    assert "| audio |" in active_section
    assert "hausKI-audio" not in active_section
    assert "historical-donor" not in active_section
    assert "| hausKI-audio | Historischer Spender" in matrix
    detailed = (ROOT / "docs/vision/heimgewebe-v2-detailed.md").read_text(encoding="utf-8")
    blueprint = (ROOT / "docs/vision/IDEal_Blueprint.mmd").read_text(encoding="utf-8")
    assert "Status: historisch und nicht normativ" in detailed
    assert "STATUS: historical-non-normative" in blueprint


def test_rollout_routes_current_work_to_audio_only() -> None:
    rollout = (ROOT / ".github/ISSUE_TEMPLATE/rollout.md").read_text(encoding="utf-8")
    assert "- [ ] **audio**" in rollout
    assert "- [ ] **hausKI-audio**" not in rollout
    assert "historischer Vertrag" in rollout


def test_audit_is_revision_bound_and_classifies_every_current_reference() -> None:
    audit = json.loads(
        (ROOT / "reports/audio-transition/hauski-audio-consumer-audit.v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["task_id"] == "OPERATOR-ECOSYSTEM-REDUNDANCY-V1-T070"
    assert audit["producer_consumer_assessment"]["current_producers"] == []
    assert audit["producer_consumer_assessment"]["current_consumers"] == []
    paths = {entry["path"] for entry in audit["references"]}
    required = {
        "contracts/audio.events.schema.json",
        "reports/integrity/sources.v1.json",
        "scripts/fleet/renovate_policy.py",
        "ai-contexts/hausKI-audio.ai-context.yml",
        "ai-contexts/audio.ai-context.yml",
        "fleet/repos.txt",
        "fleet/repos.yml",
        ".github/ISSUE_TEMPLATE/rollout.md",
        "docs/vision/IDEal_Blueprint.mmd",
        "docs/vision/heimgewebe-v2-detailed.md",
        "docs/repo-matrix.md",
        "docs/_generated/fleet.md",
        "Makefile",
    }
    assert required <= paths
