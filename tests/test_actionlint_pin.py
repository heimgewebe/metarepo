from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "tools" / "actionlint-pin.sh"
SEMVER = ROOT / "scripts" / "lib" / "semver.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _fixture(tmp_path: Path, *, checksum_mode: str = "valid") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "scripts" / "tools").mkdir(parents=True)
    (repo / "scripts" / "lib").mkdir(parents=True)
    (repo / "tools" / "bin").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "tools" / "actionlint-pin.sh")
    shutil.copy2(SEMVER, repo / "scripts" / "lib" / "semver.sh")
    (repo / "toolchain.versions.yml").write_text('actionlint: "v1.7.5"\n', encoding="utf-8")

    payload = tmp_path / "payload"
    payload.mkdir()
    actionlint = payload / "actionlint"
    _write_executable(
        actionlint,
        "#!/usr/bin/env sh\n"
        'if [ "${1:-}" = "-version" ]; then printf "1.7.5\\n"; exit 0; fi\n'
        'exit 0\n',
    )
    archive = tmp_path / "actionlint_1.7.5_linux_amd64.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(actionlint, arcname="actionlint")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    fakebin = tmp_path / "fakebin"
    fakebin.mkdir()
    _write_executable(
        fakebin / "uname",
        "#!/usr/bin/env sh\n"
        'case "${1:-}" in -s) printf "Linux\\n";; -m) printf "x86_64\\n";; *) exit 2;; esac\n',
    )
    curl_log = tmp_path / "curl.log"
    checksum_name = "actionlint_1.7.5_checksums.txt"
    filename = archive.name
    if checksum_mode == "valid":
        checksum_body = f"{digest}  {filename}\n"
        checksum_exit = 0
    elif checksum_mode == "mismatch":
        checksum_body = f"{'0' * 64}  {filename}\n"
        checksum_exit = 0
    elif checksum_mode == "missing_entry":
        checksum_body = f"{digest}  other.tar.gz\n"
        checksum_exit = 0
    elif checksum_mode == "duplicate_entry":
        checksum_body = f"{digest}  {filename}\n{digest}  {filename}\n"
        checksum_exit = 0
    elif checksum_mode == "unavailable":
        checksum_body = ""
        checksum_exit = 22
    else:
        raise AssertionError(checksum_mode)

    curl_script = f"""#!/usr/bin/env python3
import pathlib
import shutil
import sys

args = sys.argv[1:]
url = next(arg for arg in args if arg.startswith("https://"))
out = pathlib.Path(args[args.index("-o") + 1])
with pathlib.Path({str(curl_log)!r}).open("a", encoding="utf-8") as handle:
    handle.write(url + "\\n")
if url.endswith({checksum_name!r}):
    if {checksum_exit} != 0:
        raise SystemExit({checksum_exit})
    out.write_text({checksum_body!r}, encoding="utf-8")
else:
    shutil.copyfile({str(archive)!r}, out)
"""
    _write_executable(fakebin / "curl", curl_script)
    return repo, fakebin


def _run(repo: Path, fakebin: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{fakebin}:{env['PATH']}"
    return subprocess.run(
        ["bash", "scripts/tools/actionlint-pin.sh", "ensure"],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_uses_exact_official_checksum_asset_and_installs_verified_binary(tmp_path: Path) -> None:
    repo, fakebin = _fixture(tmp_path, checksum_mode="valid")

    result = _run(repo, fakebin)

    assert result.returncode == 0, result.stderr
    installed = repo / "tools" / "bin" / "actionlint"
    assert installed.is_file()
    assert subprocess.check_output([str(installed), "-version"], text=True).strip() == "1.7.5"
    urls = (tmp_path / "curl.log").read_text(encoding="utf-8").splitlines()
    assert urls == [
        "https://github.com/rhysd/actionlint/releases/download/v1.7.5/actionlint_1.7.5_linux_amd64.tar.gz",
        "https://github.com/rhysd/actionlint/releases/download/v1.7.5/actionlint_1.7.5_checksums.txt",
    ]


@pytest.mark.parametrize(
    ("mode", "message"),
    [
        ("unavailable", "Prüfsummen-Download fehlgeschlagen"),
        ("missing_entry", "genau einen Eintrag"),
        ("duplicate_entry", "genau einen Eintrag"),
        ("mismatch", "Checksum-Fehler"),
    ],
)
def test_checksum_failures_block_installation(tmp_path: Path, mode: str, message: str) -> None:
    repo, fakebin = _fixture(tmp_path, checksum_mode=mode)

    result = _run(repo, fakebin)

    assert result.returncode != 0
    assert message in result.stderr
    assert not (repo / "tools" / "bin" / "actionlint").exists()

def test_checksum_failure_preserves_existing_binary(tmp_path: Path) -> None:
    repo, fakebin = _fixture(tmp_path, checksum_mode="mismatch")
    installed = repo / "tools" / "bin" / "actionlint"
    original = b"existing-incompatible-actionlint\n"
    installed.write_bytes(original)
    installed.chmod(0o755)

    result = _run(repo, fakebin)

    assert result.returncode != 0
    assert "Checksum-Fehler" in result.stderr
    assert installed.read_bytes() == original

