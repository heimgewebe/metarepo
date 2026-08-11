"""Guard the identity-bound contract source manifest producer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
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
CHRONIK_SCHEMA = "contracts/chronik/event.batch.v1.schema.json"
BASE_EVENT_SCHEMA = "contracts/events/base.event.schema.json"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    )
    return result.stdout


def _write_schema(repo: Path, relative: str, payload: object) -> None:
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def test_chronik_consumer_binds_transitive_cross_namespace_reference(tmp_path):
    repo = _source_repo(tmp_path)
    _write_schema(repo, BASE_EVENT_SCHEMA, {"title": "base event", "type": "object"})
    _write_schema(
        repo,
        CHRONIK_SCHEMA,
        {
            "title": "event batch",
            "type": "array",
            "items": {"$ref": "../events/base.event.schema.json"},
        },
    )
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add chronik schema dependency")
    out_dir = tmp_path / "chronik-archive"

    assert (
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "chronik",
            ]
        )
        == 0
    )

    manifest = json.loads((out_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert set(manifest["schemas"]) == {CHRONIK_SCHEMA, BASE_EVENT_SCHEMA}
    for relative in manifest["schemas"]:
        committed = _git_bytes(repo, "show", f"HEAD:{relative}")
        assert (out_dir / "content" / relative).read_bytes() == committed
        assert manifest["schemas"][relative] == hashlib.sha256(committed).hexdigest()


def test_local_ref_closure_handles_fragments_normalization_external_uris_and_cycles(
    tmp_path,
):
    repo = _source_repo(tmp_path)
    first = "contracts/cycle/a.schema.json"
    second = "contracts/events/cycle-b.schema.json"
    _write_schema(
        repo,
        first,
        {
            "$defs": {
                "local": {"type": "string"},
                "self": {"$ref": "#/$defs/local"},
            },
            "allOf": [
                {"$ref": "../events/./cycle-b.schema.json#/$defs/value"},
                {
                    "$ref": "https://example.invalid/contracts/not-local.schema.json"
                },
            ],
        },
    )
    _write_schema(
        repo,
        second,
        {
            "$defs": {"value": {"type": "integer"}},
            "allOf": [{"$ref": "../cycle/a.schema.json"}],
        },
    )
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add cyclic schema references")
    out_dir = tmp_path / "cycle-archive"

    assert (
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(out_dir),
                "--consumer",
                "cycle",
            ]
        )
        == 0
    )

    manifest = json.loads((out_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert set(manifest["schemas"]) == {first, second}


@pytest.mark.parametrize(
    ("reference", "code"),
    [
        ("../../outside.schema.json", "SCHEMA_REF_ESCAPE"),
        ("../events/missing.schema.json", "SCHEMA_REF_MISSING"),
        ("../events/%2e%2e/secret.schema.json", "SCHEMA_REF_INVALID"),
        ("../events/base.event.schema.json?revision=worktree", "SCHEMA_REF_INVALID"),
    ],
)
def test_invalid_missing_or_escaping_local_refs_fail_closed(tmp_path, reference, code):
    repo = _source_repo(tmp_path)
    _write_schema(
        repo,
        "contracts/broken/root.schema.json",
        {"$ref": reference},
    )
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add invalid schema reference")

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "broken",
            ]
        )
    assert excinfo.value.code == code


def test_non_string_ref_fails_closed(tmp_path):
    repo = _source_repo(tmp_path)
    _write_schema(repo, "contracts/broken/root.schema.json", {"$ref": 42})
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add malformed schema reference")

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "broken",
            ]
        )
    assert excinfo.value.code == "SCHEMA_REF_INVALID"


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


@pytest.mark.parametrize("ignore_source", ["gitignore", "info-exclude"])
def test_ignored_schemas_are_never_selected_or_read_from_the_worktree(
    tmp_path, ignore_source
):
    repo = _source_repo(tmp_path)
    ignored = "contracts/heim-pc/ignored.schema.json"
    if ignore_source == "gitignore":
        (repo / ".gitignore").write_text(f"/{ignored}\n", encoding="utf-8")
        _git(repo, "add", ".gitignore")
        _git(repo, "commit", "-m", "ignore generated schemas")
    else:
        (repo / ".git/info").mkdir(exist_ok=True)
        (repo / ".git/info/exclude").write_text(f"/{ignored}\n", encoding="utf-8")
    _write_schema(repo, ignored, {"title": "must not be attested"})

    assert _git(repo, "status", "--porcelain=v1", "--untracked-files=all") == ""
    assert ignored in _git(repo, "status", "--short", "--ignored")

    manifest = _emit(repo, tmp_path / "consumer-archive")
    assert ignored not in manifest["schemas"]
    assert not (tmp_path / "consumer-archive/content" / ignored).exists()

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "explicit-archive"),
                "--schema",
                ignored,
            ]
        )
    assert excinfo.value.code == "SCHEMA_NOT_TRACKED"


def test_payload_bytes_come_from_head_even_when_git_hides_worktree_drift(tmp_path):
    repo = _source_repo(tmp_path)
    committed = _git_bytes(repo, "show", f"HEAD:{ZONES_SCHEMA}")
    _git(repo, "update-index", "--assume-unchanged", ZONES_SCHEMA)
    (repo / ZONES_SCHEMA).write_text('{"title":"worktree only"}\n', encoding="utf-8")
    assert _git(repo, "status", "--porcelain=v1", "--untracked-files=all") == ""

    out_dir = tmp_path / "archive"
    manifest = _emit(repo, out_dir)

    assert (out_dir / "content" / ZONES_SCHEMA).read_bytes() == committed
    assert manifest["schemas"][ZONES_SCHEMA] == hashlib.sha256(committed).hexdigest()


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


def test_invalid_source_kind_has_a_typed_cli_failure(tmp_path, capsys):
    repo = _source_repo(tmp_path)

    exit_code = main(
        [
            "--source",
            str(repo),
            "--out-dir",
            str(tmp_path / "out"),
            "--consumer",
            "heim-pc",
            "--source-kind",
            "mutable_worktree",
        ]
    )

    assert exit_code == 2
    assert capsys.readouterr().err.startswith("SOURCE_KIND_INVALID: ")


def test_content_root_cannot_collide_with_manifest_path(tmp_path):
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
                "--content-root",
                f"{MANIFEST_NAME}/content",
            ]
        )
    assert excinfo.value.code == "CONTENT_ROOT_INVALID"
    assert not (tmp_path / "out").exists()


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
        ("contracts/heim-pc/README.md", "SCHEMA_PATH_INVALID"),
        ("contracts/heim-pc/absent.schema.json", "SCHEMA_NOT_TRACKED"),
        ("contracts/heim-pc", "SCHEMA_PATH_INVALID"),
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


def test_consumer_selection_rejects_non_canonical_tracked_schema_path(tmp_path):
    repo = _source_repo(tmp_path)
    _write_schema(repo, "contracts/odd/not canonical.schema.json", {"type": "object"})
    _git(repo, "add", "contracts")
    _git(repo, "commit", "-m", "add non-canonical schema path")

    with pytest.raises(ManifestError) as excinfo:
        run(
            [
                "--source",
                str(repo),
                "--out-dir",
                str(tmp_path / "out"),
                "--consumer",
                "odd",
            ]
        )
    assert excinfo.value.code == "SCHEMA_PATH_INVALID"


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


@pytest.mark.parametrize("overwrite", [False, True])
def test_materialize_rejects_non_directory_content_root_without_traceback(
    tmp_path, capsys, overwrite
):
    repo = _source_repo(tmp_path)
    out_dir = tmp_path / "cache"
    out_dir.mkdir()
    (out_dir / "content").write_text("not a directory\n", encoding="utf-8")
    argv = [
        "--source",
        str(repo),
        "--out-dir",
        str(out_dir),
        "--consumer",
        "heim-pc",
    ]
    if overwrite:
        argv.append("--overwrite")

    assert main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("CONTENT_ROOT_INVALID_TYPE: ")
    assert "Traceback" not in captured.err


def _replace_content_root_with_file(out_dir: Path) -> None:
    shutil.rmtree(out_dir / "content")
    (out_dir / "content").write_text("not a directory\n", encoding="utf-8")


def _replace_manifest_with_directory(out_dir: Path) -> None:
    (out_dir / MANIFEST_NAME).unlink()
    (out_dir / MANIFEST_NAME).mkdir()


def _replace_bound_schema_with_symlink(out_dir: Path) -> None:
    target = out_dir / "content" / ZONES_SCHEMA
    target.unlink()
    outside = out_dir / "outside.schema.json"
    outside.write_text("{}\n", encoding="utf-8")
    target.symlink_to(outside)


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (_replace_content_root_with_file, "CONTENT_ROOT_INVALID_TYPE"),
        (_replace_manifest_with_directory, "MANIFEST_INVALID_TYPE"),
        (_replace_bound_schema_with_symlink, "CONTENT_INVALID_TYPE"),
    ],
)
def test_verify_rejects_non_regular_cache_nodes(tmp_path, mutate, code):
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
