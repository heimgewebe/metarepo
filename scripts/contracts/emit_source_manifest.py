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
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable, Sequence

EXPECTED_REPOSITORY = "heimgewebe/metarepo"
MANIFEST_NAME = "metarepo-contract-source.v1.json"
MANIFEST_SCHEMA_PATH = "contracts/contract.source.manifest.schema.json"
SOURCE_KINDS = ("detached_archive", "offline_cache")
DEFAULT_CONTENT_ROOT = "content"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
RELATIVE_POSIX = re.compile(r"^(?!.*(^|/)\.\.?(/|$))[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")


class ManifestError(RuntimeError):
    """Stable, typed contract source manifest failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        stderr = getattr(exc, "stderr", "") or ""
        raise ManifestError("SOURCE_NOT_GIT", stderr.strip() or str(exc)) from exc
    return result.stdout.strip()


def _repository_identity(origin: str) -> str:
    """Return owner/repo only for an explicit github.com Git remote URL."""

    raw = origin.strip()
    if not raw:
        return ""
    if "://" in raw:
        from urllib.parse import urlparse

        parsed = urlparse(raw)
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


def _safe_join(root: Path, relative: str) -> Path:
    try:
        root_resolved = root.resolve(strict=True)
        target = (root_resolved / relative).resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise ManifestError("SCHEMA_MISSING", f"schema is unavailable: {relative}") from exc
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise ManifestError(
            "SCHEMA_PATH_ESCAPE", f"schema escapes source root: {relative}"
        ) from exc
    if not target.is_file():
        raise ManifestError(
            "SCHEMA_MISSING", f"schema is not a regular file: {relative}"
        )
    return target


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

    origin = _run_git(root, "config", "--get", "remote.origin.url")
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

    if _run_git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ManifestError(
            "SOURCE_DIRTY",
            "a manifest binds immutable bytes; the Metarepo source must be clean. "
            "Commit or stash local changes, or use the Git-checkout resolver path instead.",
        )

    return root, head


def select_schemas(
    root: Path, consumers: Sequence[str], schemas: Sequence[str]
) -> list[str]:
    """Expand consumer namespaces and explicit paths into one sorted schema set."""

    selected: set[str] = set()

    for consumer in consumers:
        name = _relative_path(consumer, "CONSUMER_INVALID")
        if "/" in name:
            raise ManifestError(
                "CONSUMER_INVALID", f"consumer must be a single path segment: {consumer!r}"
            )
        namespace = root / "contracts" / name
        if not namespace.is_dir():
            raise ManifestError(
                "CONSUMER_UNKNOWN",
                f"no canonical contract namespace contracts/{name} in the bound source",
            )
        found = sorted(
            path.relative_to(root).as_posix()
            for path in namespace.rglob("*.schema.json")
            if path.is_file()
        )
        if not found:
            raise ManifestError(
                "CONSUMER_EMPTY",
                f"contracts/{name} binds no schema files in the bound source",
            )
        selected.update(found)

    for schema in schemas:
        selected.add(_relative_path(schema, "SCHEMA_PATH_INVALID"))

    if not selected:
        raise ManifestError(
            "SCHEMA_SELECTION",
            "at least one --consumer or --schema is required; an empty manifest binds nothing",
        )
    return sorted(selected)


def build_manifest(
    root: Path,
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

    payload_bytes: dict[str, bytes] = {}
    digests: dict[str, str] = {}
    for relative in schema_paths:
        data = _read_bytes(
            _safe_join(root, relative), "SCHEMA_UNREADABLE", f"cannot read {relative}"
        )
        payload_bytes[relative] = data
        digests[relative] = _sha256(data)

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


def _materialize(
    content_dir: Path, payload_bytes: dict[str, bytes], overwrite: bool
) -> None:
    if content_dir.exists():
        if any(content_dir.iterdir()) and not overwrite:
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


def _verify(
    out_dir: Path,
    content_root: str,
    manifest_bytes: bytes,
    payload_bytes: dict[str, bytes],
) -> None:
    manifest_path = out_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ManifestError(
            "MANIFEST_MISSING", f"no manifest to verify at {manifest_path}"
        )
    observed_manifest = _read_bytes(
        manifest_path, "MANIFEST_UNREADABLE", f"cannot read {manifest_path}"
    )
    if observed_manifest != manifest_bytes:
        raise ManifestError(
            "MANIFEST_DRIFT",
            "the stored manifest differs from the manifest the bound source produces",
        )

    content_dir = out_dir / content_root
    if not content_dir.is_dir():
        raise ManifestError(
            "CONTENT_ROOT_MISSING", f"content root is unavailable: {content_dir}"
        )
    for relative, data in sorted(payload_bytes.items()):
        target = content_dir / relative
        if not target.is_file():
            raise ManifestError(
                "CONTENT_MISSING", f"bound schema is absent from the cache: {relative}"
            )
        observed = _read_bytes(target, "CONTENT_UNREADABLE", f"cannot read {relative}")
        if observed != data:
            raise ManifestError(
                "CONTENT_DRIFT", f"cached schema bytes differ from the bound source: {relative}"
            )
    bound = set(payload_bytes)
    present = {
        path.relative_to(content_dir).as_posix()
        for path in content_dir.rglob("*")
        if path.is_file()
    }
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
        choices=SOURCE_KINDS,
        default="detached_archive",
        help="How the emitted source is consumed. Default: detached_archive.",
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
    schema_paths = select_schemas(root, args.consumer, args.schema)
    manifest, payload_bytes = build_manifest(
        root, commit, args.source_kind, args.content_root, schema_paths
    )
    manifest_bytes = render_manifest(manifest)
    out_dir = _resolve_out_dir(args.out_dir, root, create=not args.verify)

    if args.verify:
        _verify(out_dir, manifest["source_root"], manifest_bytes, payload_bytes)
    else:
        _materialize(out_dir / manifest["source_root"], payload_bytes, args.overwrite)
        manifest_path = out_dir / MANIFEST_NAME
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
