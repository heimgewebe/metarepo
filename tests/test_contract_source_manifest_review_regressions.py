"""Regression guards for PR #710 source-manifest review findings."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRODUCER_DIR = ROOT / "scripts" / "contracts"
if str(PRODUCER_DIR) not in sys.path:
    sys.path.insert(0, str(PRODUCER_DIR))

from emit_source_manifest import MANIFEST_NAME, main, run  # noqa: E402

ZONES_SCHEMA = "contracts/heim-pc/config/zones.schema.json"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    )
    return result.stdout


def _write_schema(repo: Path, relative: str, payload: object) -> None:
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _source_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "metarepo"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Contract Review Test")
    _git(repo, "remote", "add", "origin", "https://github.com/heimgewebe/metarepo.git")
    _write_schema(repo, ZONES_SCHEMA, {"title": "zones", "type": "object"})
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed contracts")
    return repo


def _emit(repo: Path, out_dir: Path, *extra: str) -> dict:
    assert (
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "heim-pc",
                *extra,
            ]
        )
        == 0
    )
    return json.loads((out_dir / MANIFEST_NAME).read_text(encoding="utf-8"))


def test_nested_id_base_resolves_through_committed_resource_identifier(tmp_path: Path) -> None:
    repo = _source_repo(tmp_path)
    root = "contracts/scoped/root.schema.json"
    target = "contracts/resources/actual-target.schema.json"
    resource_base = "https://schemas.example.invalid/scoped/"
    _write_schema(
        repo,
        root,
        {
            "$id": "https://schemas.example.invalid/root.schema.json",
            "$defs": {
                "scope": {
                    "$id": resource_base,
                    "$ref": "target.schema.json#/$defs/value",
                }
            },
        },
    )
    _write_schema(
        repo,
        target,
        {
            "$id": f"{resource_base}target.schema.json",
            "$defs": {"value": {"type": "string"}},
        },
    )
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add nested identifier scope")

    out_dir = tmp_path / "scoped-archive"
    assert (
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "scoped",
            ]
        )
        == 0
    )

    manifest = json.loads((out_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert set(manifest["schemas"]) == {root, target}


def test_replacement_refs_cannot_change_bound_commit_objects(tmp_path: Path) -> None:
    repo = _source_repo(tmp_path)
    original = _git(repo, "rev-parse", "HEAD")
    committed = _git_bytes(repo, "show", f"{original}:{ZONES_SCHEMA}")
    (repo / ZONES_SCHEMA).write_text(
        '{"title":"replacement bytes"}\n', encoding="utf-8"
    )
    _git(repo, "add", ZONES_SCHEMA)
    _git(repo, "commit", "-m", "create replacement commit")
    replacement = _git(repo, "rev-parse", "HEAD")
    _git(repo, "reset", "--hard", original)
    _git(repo, "update-ref", f"refs/replace/{original}", replacement)
    assert _git(repo, "replace", "-l") == original

    out_dir = tmp_path / "replacement-archive"
    manifest = _emit(repo, out_dir)

    assert manifest["commit"] == original
    assert (out_dir / "content" / ZONES_SCHEMA).read_bytes() == committed
    assert manifest["schemas"][ZONES_SCHEMA] == hashlib.sha256(committed).hexdigest()


def test_malformed_origin_url_is_a_typed_cli_failure(tmp_path: Path, capsys) -> None:
    repo = _source_repo(tmp_path)
    _git(repo, "remote", "set-url", "origin", "https://[invalid")

    exit_code = main(
        [
            "--source",
            str(repo),
            "--out-dir",
            str(tmp_path / "out"),
            "--consumer",
            "heim-pc",
        ]
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("SOURCE_WRONG_REPOSITORY: ")
    assert "Traceback" not in captured.err
