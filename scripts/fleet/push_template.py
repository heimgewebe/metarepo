#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile, textwrap
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:
    print("ERROR: PyYAML required (pip install pyyaml) – aborting.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
FLEET = ROOT / "fleet" / "repos.yml"

DEFAULT_BRANCH_NAME = "feat/agents-and-contracts-wave-1"
PR_TITLE = "feat: adopt agent-kit + contracts (wave 1)"
PR_BODY = textwrap.dedent("""\
  This PR introduces the **agent-kit** skeleton and the base **contracts**.

  - add `templates/agent-kit/**`
  - add `contracts/agent.tool.schema.json`
  - add `contracts/intent_event.schema.json` (leitstand only)
  - docs: linked from metarepo

  Fleet wave-1 rollout. Label: `fleet/wave-1`.
""")

def sh(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=check, text=True)


def ensure_git_identity(repo_dir: Path) -> None:
    """Ensure git user.name / user.email exist for committing."""

    def _get(cfg: str) -> str:
        result = subprocess.run(
            ["git", "config", "--get", cfg],
            cwd=repo_dir,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""

    if not _get("user.name"):
        sh(["git", "config", "user.name", "heimgewebe-bot"], cwd=repo_dir)
    if not _get("user.email"):
        sh(["git", "config", "user.email", "bot@users.noreply.github.com"], cwd=repo_dir)


def try_label(repo_dir: Path, label: str) -> None:
    """Best-effort PR labeling."""

    subprocess.run(["gh", "pr", "edit", "--add-label", label], cwd=repo_dir)

def ensure_gh():
    try:
        sh(["gh", "--version"])
    except Exception:
        print("ERROR: GitHub CLI `gh` not found.", file=sys.stderr)
        sys.exit(2)
    # auth check (non-fatal)
    try:
        sh(["gh", "auth", "status"])
    except Exception:
        print("WARN: `gh auth status` non-zero; make sure you are logged in.", file=sys.stderr)
    # ensure rollout label exists (best-effort)
    try:
        sh([
            "gh",
            "label",
            "create",
            "fleet/wave-1",
            "--description",
            "metarepo fleet rollout",
            "--color",
            "0E8A16",
        ],
           check=False)
    except Exception:
        pass

def load_repos(repo_single: str | None) -> list[dict]:
    if repo_single:
        org_repo = repo_single.strip()
        if not org_repo or "/" not in org_repo:
            print("ERROR: --repo must be like org/name", file=sys.stderr)
            sys.exit(2)
        return [{"name": org_repo, "default_branch": "main"}]
    if not FLEET.exists():
        print(f"ERROR: {FLEET} not found.", file=sys.stderr)
        sys.exit(2)
    data = yaml.safe_load(FLEET.read_text(encoding="utf-8")) or {}
    repos = data.get("repos", [])
    if not repos:
        print("ERROR: no repos configured in fleet/repos.yml", file=sys.stderr)
        sys.exit(2)
    return repos

def copy_into(src: Path, dst: Path):
    if src.is_dir():
        if dst.exists():
            # copytree can't merge; do manual copy
            for p in src.rglob("*"):
                rel = p.relative_to(src)
                target = dst / rel
                if p.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, target)
        else:
            shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def determine_copies(paths: list[str], repo_name: str) -> list[tuple[Path, Path]]:
    copies: list[tuple[Path, Path]] = []
    for rel in paths:
        src = ROOT / rel
        if not src.exists():
            print(f"WARN: path not found in metarepo: {rel}", file=sys.stderr)
            continue
        # Map sources to conventional destinations inside the target repos
        if src.match("templates/agent-kit"):
            copies.append((src, Path("templates/agent-kit")))
        elif src.match("contracts"):
            # only pick the files we want to propagate now
            for f in src.glob("*.schema.json"):
                if f.name == "agent.tool.schema.json":
                    copies.append((f, Path("contracts") / f.name))
                if f.name == "intent_event.schema.json" and repo_name.endswith("/chronik"):
                    copies.append((f, Path("contracts") / f.name))
        else:
            # default: mirror relative path
            copies.append((src, Path(rel)))
    return copies

def run(repo_single: str | None, paths: list[str], message: str, branch: str, dry_run: bool):
    ensure_gh()
    repos = load_repos(repo_single)
    if not paths:
        print("ERROR: no --paths specified", file=sys.stderr)
        sys.exit(2)

    with tempfile.TemporaryDirectory(prefix="fleet_") as tmpdir:
        tmp = Path(tmpdir)
        for entry in repos:
            name = entry["name"]
            default_branch = entry.get("default_branch", "main")
            print(f"\n=== Processing {name} (base: {default_branch}) ===")
            repo_dir = tmp / name.replace("/", "__")
            repo_dir.mkdir(parents=True, exist_ok=True)

            sh(["gh", "repo", "clone", name, str(repo_dir)])
            sh(["git", "checkout", default_branch], cwd=repo_dir)
            # create new branch
            # if already exists locally, reset; if remote exists, gh will convert push into update
            sh(["git", "checkout", "-B", branch], cwd=repo_dir)
            ensure_git_identity(repo_dir)

            copies = determine_copies(paths, name)
            changed = False
            for src, dst in copies:
                target = repo_dir / dst
                print(f"  + copy {src.relative_to(ROOT)} -> {dst}")
                copy_into(src, target)
                changed = True

            if not changed:
                print("  = nothing to copy; skipping commit/PR")
                continue

            # git add / commit
            sh(["git", "add", "-A"], cwd=repo_dir)
            # avoid empty commit
            rc = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir)
            if rc.returncode == 0:
                print("  = no staged changes; skipping push/PR")
                continue

            commit_msg = message or PR_TITLE
            sh(["git", "commit", "-m", commit_msg], cwd=repo_dir)

            if dry_run:
                print("  = dry-run: not pushing / no PR opened")
                continue

            sh(["git", "push", "-u", "origin", branch], cwd=repo_dir)
            pr_view = subprocess.run(
                ["gh", "pr", "view", "--head", branch, "--json", "number,state"],
                cwd=repo_dir,
                text=True,
                capture_output=True,
            )
            if pr_view.returncode != 0 or not pr_view.stdout.strip():
                sh([
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    PR_TITLE,
                    "--body",
                    PR_BODY,
                    "--base",
                    default_branch,
                ], cwd=repo_dir, check=False)
            else:
                sh([
                    "gh",
                    "pr",
                    "edit",
                    "--body",
                    PR_BODY,
                ], cwd=repo_dir, check=False)
            try_label(repo_dir, "fleet/wave-1")
            print(f"  ✓ PR created for {name}")

def main():
    ap = argparse.ArgumentParser(description="Push agent-kit + contracts to fleet as PRs.")
    ap.add_argument("--repo", help="single repo (e.g. heimgewebe/hausKI)")
    ap.add_argument("--paths", nargs="+", default=[], help="paths to copy from metarepo")
    ap.add_argument("--message", default=PR_TITLE, help="commit message")
    ap.add_argument("--branch", default=DEFAULT_BRANCH_NAME, help="target branch name")
    ap.add_argument("--dry-run", action="store_true", help="do not push or open PRs")
    args = ap.parse_args()
    run(args.repo, args.paths, args.message, args.branch, args.dry_run)

if __name__ == "__main__":
    main()
