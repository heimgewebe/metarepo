#!/usr/bin/env python3
"""Emit an identity-bound contract source manifest for non-Git consumers.

Consumers resolve canonical Metarepo contracts either from an explicit Git
checkout or from a manifest that binds a detached archive / approved offline
cache to repository identity, commit and per-schema SHA-256. This producer is
the reproducible way to create that manifest: everything is taken from explicit
arguments and from an identity-verified, clean Metarepo checkout. No ambient
sibling directory, environment variable or shell initialisation is consulted.

The manifest establishes provenance of bytes. It does not establish semantic
contract validity, consumer compatibility or permission to publish.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import heapq
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
import subprocess
import sys
from typing import Any, Iterable, Sequence
from urllib.parse import urldefrag, urljoin, urlsplit

EXPECTED_REPOSITORY = "heimgewebe/metarepo"
MANIFEST_NAME = "metarepo-contract-source.v1.json"
MANIFEST_SCHEMA_PATH = "contracts/contract.source.manifest.schema.json"
SOURCE_KINDS = ("detached_archive", "offline_cache")
DEFAULT_CONTENT_ROOT = "content"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
RELATIVE_POSIX = re.compile(r"^(?!.*(^|/)\.\.?(/|$))[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")

SCHEMA_VALUE_KEYWORDS = frozenset(
    {
        "additionalProperties",
        "contains",
        "contentSchema",
        "else",
        "if",
        "items",
        "not",
        "propertyNames",
        "then",
        "unevaluatedItems",
        "unevaluatedProperties",
    }
)
SCHEMA_ARRAY_KEYWORDS = frozenset({"allOf", "anyOf", "oneOf", "prefixItems"})
SCHEMA_MAP_KEYWORDS = frozenset(
    {"$defs", "dependentSchemas", "patternProperties", "properties"}
)


class ManifestError(RuntimeError):
    """Stable, typed contract source manifest failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class GitTreeEntry:
    """One path pinned to an immutable object in the selected commit."""

    mode: str
    kind: str
    object_id: str


def _git_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def _run_git(root: Path, *args: str, absent_ok: bool = False) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            text=True,
            capture_output=True,
            env=_git_environment(),
        )
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        if (
            absent_ok
            and isinstance(exc, subprocess.CalledProcessError)
            and exc.returncode == 1
            and not (exc.stdout or "").strip()
            and not (exc.stderr or "").strip()
        ):
            return ""
        stderr = getattr(exc, "stderr", "") or ""
        raise ManifestError("SOURCE_NOT_GIT", stderr.strip() or str(exc)) from exc
    return result.stdout.strip()


def _run_git_bytes(
    root: Path, *args: str, code: str = "SOURCE_NOT_GIT", detail: str = "Git read failed"
) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            env=_git_environment(),
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        stderr = getattr(exc, "stderr", b"") or b""
        if isinstance(stderr, bytes):
            error_detail = stderr.decode("utf-8", errors="replace").strip()
        else:
            error_detail = str(stderr).strip()
        raise ManifestError(code, error_detail or f"{detail}: {exc}") from exc
    return result.stdout


def _repository_identity(origin: str) -> str:
    """Return owner/repo only for an explicit github.com Git remote URL."""

    raw = origin.strip()
    if not raw:
        return ""
    if "://" in raw:
        from urllib.parse import urlparse

        try:
            parsed = urlparse(raw)
        except ValueError:
            return ""
        if (parsed.hostname or "").lower() != "github.com":
            return ""
        if parsed.scheme.lower() not in {"https", "ssh", "git"}:
            return ""
        if parsed.query or parsed.fragment:
            return ""
        path = parsed.path
    elif ":" in raw:
        authority, candidate = raw.split(":", 1)
        if authority.rsplit("@", 1)[-1].lower() != "github.com":
            return ""
        path = candidate
    else:
        # A bare owner/repo string is never proof of a checkout's remote identity.
        return ""

    normalized = path.strip("/")
    if normalized.lower().endswith(".git"):
        normalized = normalized[:-4]
    parts = normalized.split("/")
    if len(parts) != 2 or not all(parts):
        return ""
    return normalized.lower()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path: Path, code: str, detail: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ManifestError(code, f"{detail}: {exc}") from exc


def _relative_path(value: str, code: str) -> str:
    if not RELATIVE_POSIX.fullmatch(value):
        raise ManifestError(
            code, f"must be a normalized relative POSIX path: {value!r}"
        )
    return PurePosixPath(value).as_posix()


def resolve_source(source_path: str, expected_commit: str | None) -> tuple[Path, str]:
    """Resolve one explicit, clean, identity-bound Metarepo checkout."""

    try:
        root = Path(source_path).expanduser().resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise ManifestError(
            "SOURCE_MISSING", f"explicit Metarepo source is unavailable: {source_path}"
        ) from exc
    if not root.is_dir():
        raise ManifestError("SOURCE_NOT_GIT", f"not a directory: {root}")

    try:
        top = Path(_run_git(root, "rev-parse", "--show-toplevel")).resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise ManifestError(
            "SOURCE_NOT_GIT", f"cannot resolve Git repository root: {root}"
        ) from exc
    if top != root:
        raise ManifestError(
            "SOURCE_NOT_REPOSITORY_ROOT",
            f"explicit source must be the Git repository root: {root}",
        )

    origin = _run_git(
        root, "config", "--get", "remote.origin.url", absent_ok=True
    )
    if _repository_identity(origin) != EXPECTED_REPOSITORY:
        raise ManifestError(
            "SOURCE_WRONG_REPOSITORY",
            f"expected GitHub repository {EXPECTED_REPOSITORY}; "
            "the explicit origin did not resolve to that canonical identity",
        )

    head = _run_git(root, "rev-parse", "HEAD").lower()
    if not HEX40.fullmatch(head):
        raise ManifestError(
            "SOURCE_COMMIT_INVALID", "HEAD is not a full 40-hex lowercase commit"
        )
    if expected_commit is not None:
        expected = expected_commit.strip().lower()
        if not HEX40.fullmatch(expected):
            raise ManifestError(
                "EXPECTED_COMMIT_INVALID",
                "expected commit must be exactly 40 lowercase hex characters",
            )
        if head != expected:
            raise ManifestError(
                "SOURCE_COMMIT_MISMATCH", f"expected {expected}, observed {head}"
            )

    _validate_commit_objects(root, head)

    if _run_git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ManifestError(
            "SOURCE_DIRTY",
            "a manifest binds immutable bytes; the Metarepo source must be clean. "
            "Commit or stash local changes, or use the Git-checkout resolver path instead.",
        )

    return root, head


def _git_object_id(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _validate_commit_objects(root: Path, commit: str) -> None:
    """Validate the literal commit and root-tree objects without replacements."""

    commit_data = _run_git_bytes(
        root,
        "cat-file",
        "commit",
        commit,
        code="SOURCE_COMMIT_INVALID",
        detail=f"cannot read commit object {commit}",
    )
    if _git_object_id("commit", commit_data) != commit:
        raise ManifestError(
            "SOURCE_COMMIT_INVALID", "HEAD does not name the unchanged commit object"
        )
    first_line = commit_data.split(b"\n", 1)[0]
    if not first_line.startswith(b"tree "):
        raise ManifestError("SOURCE_COMMIT_INVALID", "commit has no root tree")
    try:
        tree = first_line.removeprefix(b"tree ").decode("ascii")
    except UnicodeDecodeError as exc:
        raise ManifestError(
            "SOURCE_COMMIT_INVALID", "commit has an invalid root tree"
        ) from exc
    if not HEX40.fullmatch(tree):
        raise ManifestError("SOURCE_COMMIT_INVALID", "commit has an invalid root tree")
    tree_data = _run_git_bytes(
        root,
        "cat-file",
        "tree",
        tree,
        code="SOURCE_COMMIT_INVALID",
        detail=f"cannot read root tree object {tree}",
    )
    if _git_object_id("tree", tree_data) != tree:
        raise ManifestError(
            "SOURCE_COMMIT_INVALID", "commit does not bind an unchanged root-tree object"
        )


def _commit_tree(root: Path, commit: str) -> dict[str, GitTreeEntry]:
    """Read the contracts tree from one commit, never from the working tree."""

    raw_tree = _run_git_bytes(
        root,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        commit,
        "--",
        "contracts",
        code="SOURCE_COMMIT_INVALID",
        detail=f"cannot inspect contract tree at {commit}",
    )
    entries: dict[str, GitTreeEntry] = {}
    for raw_entry in raw_tree.split(b"\0"):
        if not raw_entry:
            continue
        try:
            raw_metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, kind, object_id = raw_metadata.decode("ascii").split(" ")
            relative = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise ManifestError(
                "SCHEMA_PATH_INVALID",
                "the committed contracts tree contains an unrepresentable path",
            ) from exc
        entries[relative] = GitTreeEntry(mode, kind, object_id)
    return entries


def select_schemas(
    tree: dict[str, GitTreeEntry], consumers: Sequence[str], schemas: Sequence[str]
) -> list[str]:
    """Expand selections against paths tracked by the bound commit."""

    selected: set[str] = set()

    for consumer in consumers:
        name = _relative_path(consumer, "CONSUMER_INVALID")
        if "/" in name:
            raise ManifestError(
                "CONSUMER_INVALID", f"consumer must be a single path segment: {consumer!r}"
            )
        namespace = f"contracts/{name}/"
        namespace_paths = sorted(path for path in tree if path.startswith(namespace))
        if not namespace_paths:
            raise ManifestError(
                "CONSUMER_UNKNOWN",
                f"no canonical contract namespace contracts/{name} in the bound source",
            )
        found = [
            _relative_path(path, "SCHEMA_PATH_INVALID")
            for path in namespace_paths
            if path.endswith(".schema.json")
        ]
        if not found:
            raise ManifestError(
                "CONSUMER_EMPTY",
                f"contracts/{name} binds no schema files in the bound source",
            )
        selected.update(found)

    for schema in schemas:
        relative = _relative_path(schema, "SCHEMA_PATH_INVALID")
        if not relative.endswith(".schema.json"):
            raise ManifestError(
                "SCHEMA_PATH_INVALID",
                f"explicit selection is not a canonical schema path: {relative}",
            )
        if relative not in tree:
            raise ManifestError(
                "SCHEMA_NOT_TRACKED",
                f"schema is not tracked by the bound commit: {relative}",
            )
        selected.add(relative)

    if not selected:
        raise ManifestError(
            "SCHEMA_SELECTION",
            "at least one --consumer or --schema is required; an empty manifest binds nothing",
        )
    return sorted(selected)


def _read_schema_blob(
    root: Path,
    tree: dict[str, GitTreeEntry],
    relative: str,
    *,
    referrer: str | None = None,
) -> bytes:
    entry = tree.get(relative)
    if entry is None:
        if referrer is not None:
            raise ManifestError(
                "SCHEMA_REF_MISSING",
                f"{referrer} references a schema not tracked by the bound commit: {relative}",
            )
        raise ManifestError(
            "SCHEMA_NOT_TRACKED",
            f"schema is not tracked by the bound commit: {relative}",
        )
    if entry.kind != "blob" or entry.mode not in {"100644", "100755"}:
        if entry.mode == "120000":
            raise ManifestError(
                "SCHEMA_PATH_ESCAPE",
                f"schema is a Git symlink rather than commit-bound schema bytes: {relative}",
            )
        raise ManifestError(
            "SCHEMA_NOT_REGULAR",
            f"schema is not a regular Git blob in the bound commit: {relative}",
        )
    return _run_git_bytes(
        root,
        "cat-file",
        "blob",
        entry.object_id,
        code="SCHEMA_UNREADABLE",
        detail=f"cannot read committed schema blob {relative}",
    )


def _decode_schema(relative: str, data: bytes) -> Any:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number {value}")

    try:
        text = data.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ManifestError(
            "SCHEMA_JSON_INVALID",
            f"cannot inspect local references in {relative}: {exc}",
        ) from exc


def _physical_schema_uri(relative: str) -> str:
    return f"https://metarepo.invalid/{relative}"


def _resolve_uri(referrer: str, base_uri: str, value: str, keyword: str) -> str:
    try:
        parsed = urlsplit(value)
        resolved = urljoin(base_uri, value)
        urlsplit(resolved)
    except ValueError as exc:
        raise ManifestError(
            f"SCHEMA_{keyword}_INVALID",
            f"{referrer} contains an invalid ${keyword.lower()}: {value!r}",
        ) from exc
    if not resolved or (not parsed.scheme and value.startswith("//")):
        raise ManifestError(
            f"SCHEMA_{keyword}_INVALID",
            f"{referrer} contains an invalid ${keyword.lower()}: {value!r}",
        )
    return resolved


def _schema_resources_and_references(
    relative: str, schema: Any, base_uri: str
) -> Iterable[tuple[str, str]]:
    """Yield resources and references at Draft 2020-12 schema positions."""

    if isinstance(schema, dict):
        active_base = base_uri
        if "$id" in schema:
            identifier = schema["$id"]
            if not isinstance(identifier, str):
                raise ManifestError(
                    "SCHEMA_ID_INVALID", f"{relative} contains a non-string $id"
                )
            active_base = _resolve_uri(relative, base_uri, identifier, "ID")
            document_uri, fragment = urldefrag(active_base)
            if fragment:
                raise ManifestError(
                    "SCHEMA_ID_INVALID", f"{relative} contains a fragment-bearing $id"
                )
            yield "identifier", document_uri
        for key in sorted(schema):
            value = schema[key]
            if key == "$ref":
                if not isinstance(value, str):
                    raise ManifestError(
                        "SCHEMA_REF_INVALID", f"{relative} contains a non-string $ref"
                    )
                yield "reference", _resolve_uri(relative, active_base, value, "REF")
            elif key in SCHEMA_VALUE_KEYWORDS:
                yield from _schema_resources_and_references(relative, value, active_base)
            elif key in SCHEMA_ARRAY_KEYWORDS and isinstance(value, list):
                for subschema in value:
                    yield from _schema_resources_and_references(
                        relative, subschema, active_base
                    )
            elif key in SCHEMA_MAP_KEYWORDS and isinstance(value, dict):
                for name in sorted(value):
                    yield from _schema_resources_and_references(
                        relative, value[name], active_base
                    )


def _schema_identifier_index(
    root: Path, tree: dict[str, GitTreeEntry]
) -> tuple[dict[str, str], dict[str, tuple[Any, bytes]]]:
    """Index every committed schema resource identifier deterministically."""

    identifiers: dict[str, str] = {}
    schemas: dict[str, tuple[Any, bytes]] = {}
    for relative in sorted(
        path
        for path in tree
        if path.startswith("contracts/") and path.endswith(".schema.json")
    ):
        data = _read_schema_blob(root, tree, relative)
        schema = _decode_schema(relative, data)
        schemas[relative] = (schema, data)
        physical_uri = _physical_schema_uri(relative)
        previous = identifiers.get(physical_uri)
        if previous is not None and previous != relative:
            raise ManifestError(
                "SCHEMA_ID_DUPLICATE",
                f"schema resource identifier {physical_uri!r} is bound by both "
                f"{previous} and {relative}",
            )
        identifiers[physical_uri] = relative
        for kind, identifier in _schema_resources_and_references(
            relative, schema, physical_uri
        ):
            if kind != "identifier":
                continue
            previous = identifiers.get(identifier)
            if previous is not None and previous != relative:
                raise ManifestError(
                    "SCHEMA_ID_DUPLICATE",
                    f"schema resource identifier {identifier!r} is bound by both "
                    f"{previous} and {relative}",
                )
            identifiers[identifier] = relative
    return identifiers, schemas


def _resolve_local_reference(
    referrer: str, resolved_uri: str, identifiers: dict[str, str]
) -> str | None:
    """Bind a resolved URI to a committed local resource, or classify it external."""

    try:
        document_uri, _fragment = urldefrag(resolved_uri)
        parsed = urlsplit(document_uri)
    except ValueError as exc:
        raise ManifestError(
            "SCHEMA_REF_INVALID", f"{referrer} contains an invalid $ref: {resolved_uri!r}"
        ) from exc

    indexed = identifiers.get(document_uri)
    if indexed is not None:
        return indexed

    if parsed.scheme != "https" or parsed.netloc != "metarepo.invalid":
        return None
    if not parsed.path:
        return None
    if parsed.query:
        raise ManifestError(
            "SCHEMA_REF_INVALID",
            f"{referrer} uses a query in a local $ref: {resolved_uri!r}",
        )

    path = parsed.path.removeprefix("/")
    if "\\" in path or "%" in path or "\x00" in path:
        raise ManifestError(
            "SCHEMA_REF_INVALID",
            f"{referrer} contains a non-canonical local $ref path: {resolved_uri!r}",
        )

    resolved = posixpath.normpath(path)
    if resolved == "contracts" or not resolved.startswith("contracts/"):
        raise ManifestError(
            "SCHEMA_REF_ESCAPE",
            f"{referrer} has a local $ref outside contracts/: {resolved_uri!r}",
        )
    normalized = _relative_path(resolved, "SCHEMA_REF_INVALID")
    if not normalized.endswith(".schema.json"):
        raise ManifestError(
            "SCHEMA_REF_INVALID",
            f"{referrer} does not reference a canonical schema path: {resolved_uri!r}",
        )
    return normalized


def _schema_closure(
    root: Path,
    tree: dict[str, GitTreeEntry],
    schema_paths: Iterable[str],
) -> dict[str, bytes]:
    """Return deterministic transitive local $ref closure from committed blobs."""

    identifiers, schemas = _schema_identifier_index(root, tree)
    pending = [(relative, "") for relative in schema_paths]
    heapq.heapify(pending)
    payload_bytes: dict[str, bytes] = {}
    while pending:
        relative, referrer = heapq.heappop(pending)
        if relative in payload_bytes:
            continue
        cached = schemas.get(relative)
        if cached is None:
            data = _read_schema_blob(root, tree, relative, referrer=referrer or None)
            schema = _decode_schema(relative, data)
        else:
            schema, data = cached
        payload_bytes[relative] = data
        for kind, resolved_uri in _schema_resources_and_references(
            relative, schema, _physical_schema_uri(relative)
        ):
            if kind != "reference":
                continue
            dependency = _resolve_local_reference(relative, resolved_uri, identifiers)
            if dependency is None or dependency in payload_bytes:
                continue
            heapq.heappush(pending, (dependency, relative))
    return dict(sorted(payload_bytes.items()))


def build_manifest(
    root: Path,
    tree: dict[str, GitTreeEntry],
    commit: str,
    source_kind: str,
    content_root: str,
    schema_paths: Iterable[str],
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Return the manifest payload plus the exact bytes it binds."""

    if source_kind not in SOURCE_KINDS:
        raise ManifestError(
            "SOURCE_KIND_INVALID",
            f"source_kind must be one of {', '.join(SOURCE_KINDS)}",
        )
    content = _relative_path(content_root, "CONTENT_ROOT_INVALID")
    if PurePosixPath(content).parts[0] == MANIFEST_NAME:
        raise ManifestError(
            "CONTENT_ROOT_INVALID",
            "content root must not collide with the manifest path",
        )

    payload_bytes = _schema_closure(root, tree, schema_paths)
    digests = {relative: _sha256(data) for relative, data in payload_bytes.items()}

    manifest = {
        "schema_version": 1,
        "repository": EXPECTED_REPOSITORY,
        "commit": commit,
        "source_kind": source_kind,
        "source_root": content,
        "schemas": dict(sorted(digests.items())),
    }
    return manifest, payload_bytes


def render_manifest(manifest: dict[str, Any]) -> bytes:
    """Render one canonical byte representation for identical inputs."""

    return (
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _resolve_out_dir(out_dir: str, source_root: Path, create: bool) -> Path:
    path = Path(out_dir).expanduser()
    if create:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as exc:
            raise ManifestError("OUT_DIR_INVALID", f"not a directory: {out_dir}") from exc
        except OSError as exc:
            raise ManifestError("OUT_DIR_UNWRITABLE", f"{out_dir}: {exc}") from exc
    try:
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise ManifestError("OUT_DIR_MISSING", f"output directory is unavailable: {out_dir}") from exc
    if not resolved.is_dir():
        raise ManifestError("OUT_DIR_INVALID", f"not a directory: {resolved}")
    if resolved == source_root or source_root in resolved.parents:
        raise ManifestError(
            "OUT_DIR_INSIDE_SOURCE",
            "the output directory must not live inside the bound Metarepo source",
        )
    return resolved


def _resolve_content_dir(
    out_dir: Path, content_root: str, *, error_code: str
) -> Path:
    """Resolve a lexical content root without following existing symlinks."""

    current = out_dir
    parts = PurePosixPath(content_root).parts
    for index, part in enumerate(parts):
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ManifestError(error_code, f"cannot inspect {current}: {exc}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ManifestError(
                "CONTENT_ROOT_PATH_ESCAPE",
                f"content root traverses a symlink: {current}",
            )
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise ManifestError(
                "CONTENT_ROOT_INVALID_TYPE",
                f"content root parent is not a directory: {current}",
            )
    return current


def _manifest_target_for_write(out_dir: Path) -> Path:
    manifest_path = out_dir / MANIFEST_NAME
    try:
        metadata = manifest_path.lstat()
    except FileNotFoundError:
        return manifest_path
    except OSError as exc:
        raise ManifestError(
            "OUT_DIR_UNWRITABLE", f"cannot inspect {manifest_path}: {exc}"
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ManifestError(
            "MANIFEST_INVALID_TYPE",
            f"manifest target is not a regular non-symlink file: {manifest_path}",
        )
    return manifest_path


def _materialize(
    content_dir: Path, payload_bytes: dict[str, bytes], overwrite: bool
) -> None:
    try:
        metadata = content_dir.lstat()
    except FileNotFoundError:
        metadata = None
    except OSError as exc:
        raise ManifestError("OUT_DIR_UNWRITABLE", f"{content_dir}: {exc}") from exc

    if metadata is not None:
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ManifestError(
                "CONTENT_ROOT_INVALID_TYPE",
                f"content root is not a regular directory: {content_dir}",
            )
        try:
            has_content = next(content_dir.iterdir(), None) is not None
        except OSError as exc:
            raise ManifestError("OUT_DIR_UNWRITABLE", f"{content_dir}: {exc}") from exc
        if has_content and not overwrite:
            raise ManifestError(
                "CONTENT_ROOT_NOT_EMPTY",
                f"{content_dir} already has content; pass --overwrite to replace it",
            )
        try:
            shutil.rmtree(content_dir)
        except OSError as exc:
            raise ManifestError("OUT_DIR_UNWRITABLE", f"{content_dir}: {exc}") from exc
    for relative, data in sorted(payload_bytes.items()):
        target = content_dir / relative
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except OSError as exc:
            raise ManifestError("OUT_DIR_UNWRITABLE", f"{target}: {exc}") from exc


def _regular_manifest_for_verify(out_dir: Path) -> Path:
    manifest_path = out_dir / MANIFEST_NAME
    try:
        metadata = manifest_path.lstat()
    except FileNotFoundError as exc:
        raise ManifestError(
            "MANIFEST_MISSING", f"no manifest to verify at {manifest_path}"
        ) from exc
    except OSError as exc:
        raise ManifestError(
            "MANIFEST_UNREADABLE", f"cannot inspect {manifest_path}: {exc}"
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ManifestError(
            "MANIFEST_INVALID_TYPE",
            f"manifest is not a regular non-symlink file: {manifest_path}",
        )
    return manifest_path


def _regular_cached_schema(content_dir: Path, relative: str) -> Path:
    current = content_dir
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError as exc:
            raise ManifestError(
                "CONTENT_MISSING", f"bound schema is absent from the cache: {relative}"
            ) from exc
        except OSError as exc:
            raise ManifestError(
                "CONTENT_UNREADABLE", f"cannot inspect {relative}: {exc}"
            ) from exc
        is_final = index == len(parts) - 1
        if stat.S_ISLNK(metadata.st_mode):
            raise ManifestError(
                "CONTENT_INVALID_TYPE",
                f"bound schema path traverses a symlink: {relative}",
            )
        if is_final:
            if not stat.S_ISREG(metadata.st_mode):
                raise ManifestError(
                    "CONTENT_INVALID_TYPE",
                    f"bound schema is not a regular file: {relative}",
                )
        elif not stat.S_ISDIR(metadata.st_mode):
            raise ManifestError(
                "CONTENT_INVALID_TYPE",
                f"bound schema parent is not a directory: {relative}",
            )
    return current


def _present_cache_files(content_dir: Path) -> set[str]:
    present: set[str] = set()
    pending = [content_dir]
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as exc:
            raise ManifestError(
                "CONTENT_UNREADABLE", f"cannot enumerate {directory}: {exc}"
            ) from exc
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(content_dir).as_posix()
            try:
                if entry.is_symlink():
                    raise ManifestError(
                        "CONTENT_INVALID_TYPE",
                        f"cache contains a symlink: {relative}",
                    )
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    present.add(relative)
                else:
                    raise ManifestError(
                        "CONTENT_INVALID_TYPE",
                        f"cache contains a non-regular node: {relative}",
                    )
            except OSError as exc:
                raise ManifestError(
                    "CONTENT_UNREADABLE", f"cannot inspect {relative}: {exc}"
                ) from exc
    return present


def _verify(
    out_dir: Path,
    content_root: str,
    manifest_bytes: bytes,
    payload_bytes: dict[str, bytes],
) -> None:
    manifest_path = _regular_manifest_for_verify(out_dir)
    observed_manifest = _read_bytes(
        manifest_path, "MANIFEST_UNREADABLE", f"cannot read {manifest_path}"
    )
    if observed_manifest != manifest_bytes:
        raise ManifestError(
            "MANIFEST_DRIFT",
            "the stored manifest differs from the manifest the bound source produces",
        )

    content_dir = _resolve_content_dir(
        out_dir, content_root, error_code="CONTENT_UNREADABLE"
    )
    try:
        content_metadata = content_dir.lstat()
    except FileNotFoundError as exc:
        raise ManifestError(
            "CONTENT_ROOT_MISSING", f"content root is unavailable: {content_dir}"
        ) from exc
    except OSError as exc:
        raise ManifestError(
            "CONTENT_UNREADABLE", f"cannot inspect content root {content_dir}: {exc}"
        ) from exc
    if not stat.S_ISDIR(content_metadata.st_mode):
        raise ManifestError(
            "CONTENT_ROOT_INVALID_TYPE",
            f"content root is not a regular directory: {content_dir}",
        )
    for relative, data in sorted(payload_bytes.items()):
        target = _regular_cached_schema(content_dir, relative)
        observed = _read_bytes(target, "CONTENT_UNREADABLE", f"cannot read {relative}")
        if observed != data:
            raise ManifestError(
                "CONTENT_DRIFT", f"cached schema bytes differ from the bound source: {relative}"
            )
    bound = set(payload_bytes)
    present = _present_cache_files(content_dir)
    unbound = sorted(present - bound)
    if unbound:
        raise ManifestError(
            "CONTENT_UNBOUND",
            f"the cache carries files the manifest does not bind: {', '.join(unbound)}",
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the explicit heimgewebe/metarepo Git repository root.",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory that receives the manifest and its content root.",
    )
    parser.add_argument(
        "--consumer",
        action="append",
        default=[],
        metavar="NAME",
        help="Bind every schema under contracts/NAME/ (repeatable).",
    )
    parser.add_argument(
        "--schema",
        action="append",
        default=[],
        metavar="PATH",
        help="Bind one additional schema by its path relative to the source root (repeatable).",
    )
    parser.add_argument(
        "--source-kind",
        default="detached_archive",
        help=(
            "How the emitted source is consumed "
            f"({', '.join(SOURCE_KINDS)}). Default: detached_archive."
        ),
    )
    parser.add_argument(
        "--content-root",
        default=DEFAULT_CONTENT_ROOT,
        help=f"Relative content root below --out-dir. Default: {DEFAULT_CONTENT_ROOT}.",
    )
    parser.add_argument(
        "--expected-commit",
        help="Require the bound source to be at this exact 40-hex commit.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing non-empty content root instead of failing closed.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Do not write; assert that an existing manifest and cache still match the bound source.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    root, commit = resolve_source(args.source, args.expected_commit)
    tree = _commit_tree(root, commit)
    schema_paths = select_schemas(tree, args.consumer, args.schema)
    manifest, payload_bytes = build_manifest(
        root, tree, commit, args.source_kind, args.content_root, schema_paths
    )
    manifest_bytes = render_manifest(manifest)
    out_dir = _resolve_out_dir(args.out_dir, root, create=not args.verify)

    if args.verify:
        _verify(out_dir, manifest["source_root"], manifest_bytes, payload_bytes)
    else:
        content_dir = _resolve_content_dir(
            out_dir, manifest["source_root"], error_code="OUT_DIR_UNWRITABLE"
        )
        manifest_path = _manifest_target_for_write(out_dir)
        _materialize(content_dir, payload_bytes, args.overwrite)
        try:
            manifest_path.write_bytes(manifest_bytes)
        except OSError as exc:
            raise ManifestError("OUT_DIR_UNWRITABLE", f"{manifest_path}: {exc}") from exc

    sys.stdout.write(manifest_bytes.decode("utf-8"))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return run(argv)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
