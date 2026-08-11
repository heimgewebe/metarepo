"""Guard the identity-bound contract source manifest producer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PRODUCER_DIR = ROOT / "scripts" / "contracts"
if str(PRODUCER_DIR) not in sys.path:
    sys.path.insert(0, str(PRODUCER_DIR))

from emit_source_manifest import (  # noqa: E402
    MANIFEST_NAME,
    MANIFEST_SCHEMA_PATH,
    ManifestError,
    main,
    run,
)

ZONES_SCHEMA = "contracts/heim-pc/config/zones.schema.json"
DRIFT_SCHEMA = "contracts/heim-pc/state/heim-pc.state.drift.schema.json"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def _source_repo(tmp_path: Path, origin: str = "https://github.com/heimgewebe/metarepo.git") -> Path:
    """Create a minimal stand-in for a canonical Metarepo checkout."""

    repo = tmp_path / "metarepo"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Contract Test")
    _git(repo, "remote", "add", "origin", origin)

    for relative in (ZONES_SCHEMA, DRIFT_SCHEMA, MANIFEST_SCHEMA_PATH):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative == MANIFEST_SCHEMA_PATH:
            target.write_bytes((ROOT / MANIFEST_SCHEMA_PATH).read_bytes())
        else:
            target.write_text(
                json.dumps({"title": relative, "type": "object"}, indent=2) + "\n",
                encoding="utf-8",
            )
    # A non-schema file must never be bound by a consumer namespace expansion.
    (repo / "contracts/heim-pc/README.md").write_text("consumer notes\n", encoding="utf-8")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed canonical contracts")
    return repo


def _emit(repo: Path, out_dir: Path, *extra: str) -> dict:
    payload = run(
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
    assert payload == 0
    return json.loads((out_dir / MANIFEST_NAME).read_text(encoding="utf-8"))


def test_manifest_binds_repository_commit_and_every_schema_hash(tmp_path, capsys):
    repo = _source_repo(tmp_path)
    out_dir = tmp_path / "archive"

    manifest = _emit(repo, out_dir)

    assert manifest["schema_version"] == 1
    assert manifest["repository"] == "heimgewebe/metarepo"
    assert manifest["commit"] == _git(repo, "rev-parse", "HEAD").lower()
    assert manifest["source_kind"] == "detached_archive"
    assert manifest["source_root"] == "content"
    # A consumer namespace binds its schemas and nothing else.
    assert set(manifest["schemas"]) == {ZONES_SCHEMA, DRIFT_SCHEMA}
    assert not (out_dir / "content/contracts/heim-pc/README.md").exists()

    for relative, digest in manifest["schemas"].items():
        source_bytes = (repo / relative).read_bytes()
        cached_bytes = (out_dir / "content" / relative).read_bytes()
        assert cached_bytes == source_bytes
        assert digest == hashlib.sha256(source_bytes).hexdigest()

    # The manifest is emitted on stdout as well, byte-identical to the file.
    assert capsys.readouterr().out == (out_dir / MANIFEST_NAME).read_text(encoding="utf-8")


def test_emitted_manifest_satisfies_the_published_contract(tmp_path):
    repo = _source_repo(tmp_path)
    manifest = _emit(repo, tmp_path / "archive")

    schema = json.loads((ROOT / MANIFEST_SCHEMA_PATH).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)


def test_offline_cache_round_trip_is_deterministic_and_verifiable(tmp_path):
    repo = _source_repo(tmp_path)
    out_dir = tmp_path / "cache"

    _emit(repo, out_dir, "--source-kind", "offline_cache")
    first = (out_dir / MANIFEST_NAME).read_bytes()
    _emit(repo, out_dir, "--source-kind", "offline_cache", "--overwrite")
    assert (out_dir / MANIFEST_NAME).read_bytes() == first

    assert (
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "heim-pc",
                "--source-kind",
                "offline_cache",
                "--verify",
            ]
        )
        == 0
    )


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (
            lambda out_dir: (out_dir / "content" / ZONES_SCHEMA).write_text(
                "{}\n", encoding="utf-8"
            ),
            "CONTENT_DRIFT",
        ),
        (
            lambda out_dir: (out_dir / "content" / ZONES_SCHEMA).unlink(),
            "CONTENT_MISSING",
        ),
        (
            lambda out_dir: (out_dir / "content/contracts/heim-pc/extra.json").write_text(
                "{}\n", encoding="utf-8"
            ),
            "CONTENT_UNBOUND",
        ),
        (
            lambda out_dir: (out_dir / MANIFEST_NAME).write_text("{}\n", encoding="utf-8"),
            "MANIFEST_DRIFT",
        ),
        (
            lambda out_dir: (out_dir / MANIFEST_NAME).unlink(),
            "MANIFEST_MISSING",
        ),
    ],
)
def test_verify_rejects_every_cache_divergence(tmp_path, mutate, code):
    repo = _source_repo(tmp_path)
    out_dir = tmp_path / "cache"
    _emit(repo, out_dir, "--source-kind", "offline_cache")

    mutate(out_dir)

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "heim-pc",
                "--source-kind",
                "offline_cache",
                "--verify",
            ]
        )
    assert excinfo.value.code == code


def test_dirty_source_cannot_be_bound_as_immutable(tmp_path):
    repo = _source_repo(tmp_path)
    (repo / ZONES_SCHEMA).write_text("{}\n", encoding="utf-8")

    with pytest.raises(ManifestError) as excinfo:
        run(["--source", str(repo), "--out-dir", str(tmp_path / "out"), "--consumer", "heim-pc"])
    assert excinfo.value.code == "SOURCE_DIRTY"
    assert not (tmp_path / "out").exists()


def test_untracked_file_also_makes_the_source_dirty(tmp_path):
    repo = _source_repo(tmp_path)
    (repo / "contracts/heim-pc/scratch.schema.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ManifestError) as excinfo:
        run(["--source", str(repo), "--out-dir", str(tmp_path / "out"), "--consumer", "heim-pc"])
    assert excinfo.value.code == "SOURCE_DIRTY"


@pytest.mark.parametrize(
    "origin",
    [
        "https://github.com/heimgewebe/heim-pc.git",
        "https://gitlab.com/heimgewebe/metarepo.git",
        "heimgewebe/metarepo",
        "",
    ],
)
def test_only_a_canonical_github_origin_is_accepted(tmp_path, origin):
    repo = _source_repo(tmp_path, origin="https://github.com/heimgewebe/metarepo.git")
    if origin:
        _git(repo, "remote", "set-url", "origin", origin)
    else:
        _git(repo, "remote", "remove", "origin")

    with pytest.raises(ManifestError) as excinfo:
        run(["--source", str(repo), "--out-dir", str(tmp_path / "out"), "--consumer", "heim-pc"])
    assert excinfo.value.code in {"SOURCE_WRONG_REPOSITORY", "SOURCE_NOT_GIT"}


def test_expected_commit_mismatch_fails_closed(tmp_path):
    repo = _source_repo(tmp_path)

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "heim-pc",
                "--expected-commit",
                "0" * 40,
            ]
        )
    assert excinfo.value.code == "SOURCE_COMMIT_MISMATCH"

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "heim-pc",
                "--expected-commit",
                "not-a-commit",
            ]
        )
    assert excinfo.value.code == "EXPECTED_COMMIT_INVALID"


def test_a_manifest_must_bind_something_explicitly(tmp_path):
    repo = _source_repo(tmp_path)

    with pytest.raises(ManifestError) as excinfo:
        run(["--source", str(repo), "--out-dir", str(tmp_path / "out")])
    assert excinfo.value.code == "SCHEMA_SELECTION"

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "weltgewebe",
            ]
        )
    assert excinfo.value.code == "CONSUMER_UNKNOWN"


@pytest.mark.parametrize(
    ("schema", "code"),
    [
        ("/etc/passwd", "SCHEMA_PATH_INVALID"),
        ("contracts/../../secret.json", "SCHEMA_PATH_INVALID"),
        ("contracts\\heim-pc\\zones.json", "SCHEMA_PATH_INVALID"),
        ("contracts/heim-pc/absent.schema.json", "SCHEMA_MISSING"),
        ("contracts/heim-pc", "SCHEMA_MISSING"),
    ],
)
def test_explicit_schema_paths_stay_inside_the_bound_source(tmp_path, schema, code):
    repo = _source_repo(tmp_path)

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--schema",
                schema,
            ]
        )
    assert excinfo.value.code == code


def test_symlinked_schema_escaping_the_source_is_rejected(tmp_path):
    outside = tmp_path / "outside.schema.json"
    outside.write_text("{}\n", encoding="utf-8")
    repo = _source_repo(tmp_path)
    link = repo / "contracts/heim-pc/linked.schema.json"
    link.symlink_to(outside)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add escaping link")

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--schema",
                "contracts/heim-pc/linked.schema.json",
            ]
        )
    assert excinfo.value.code == "SCHEMA_PATH_ESCAPE"


def test_output_must_not_dirty_the_bound_source(tmp_path):
    repo = _source_repo(tmp_path)

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(repo / "build" / "archive"),
                "--consumer",
                "heim-pc",
            ]
        )
    assert excinfo.value.code == "OUT_DIR_INSIDE_SOURCE"


def test_existing_cache_content_is_never_silently_replaced(tmp_path):
    repo = _source_repo(tmp_path)
    out_dir = tmp_path / "cache"
    _emit(repo, out_dir)

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "heim-pc",
            ]
        )
    assert excinfo.value.code == "CONTENT_ROOT_NOT_EMPTY"


def test_ci_style_sibling_layout_is_authoritative_only_when_named(tmp_path, monkeypatch):
    """A CI checkout next to the consumer is a path, never ambient authority."""

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    repo = _source_repo(workspace)
    (workspace / "metarepo").rename(workspace / "_metarepo")
    sibling = workspace / "_metarepo"
    consumer = workspace / "heim-pc"
    consumer.mkdir()
    monkeypatch.chdir(consumer)
    monkeypatch.setenv("METAREPO_ROOT", str(sibling))

    with pytest.raises(SystemExit):
        run(["--out-dir", str(tmp_path / "out"), "--consumer", "heim-pc"])

    manifest = _emit(sibling, tmp_path / "out")
    assert manifest["commit"] == _git(sibling, "rev-parse", "HEAD").lower()
    assert repo.name == "metarepo"


def test_cli_entry_point_reports_typed_failures_without_traceback(tmp_path, capsys):
    repo = _source_repo(tmp_path)
    (repo / ZONES_SCHEMA).write_text("{}\n", encoding="utf-8")

    exit_code = main(
        ["--source", str(repo), "--out-dir", str(tmp_path / "out"), "--consumer", "heim-pc"]
    )

    assert exit_code == 2
    assert capsys.readouterr().err.startswith("SOURCE_DIRTY: ")
