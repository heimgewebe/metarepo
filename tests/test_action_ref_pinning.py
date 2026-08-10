from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_V7_SHA = "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"


def _workflow_files():
    roots = [ROOT / ".github" / "workflows", ROOT / "templates" / ".github" / "workflows"]
    for root in roots:
        if root.exists():
            yield from sorted(root.rglob("*.yml"))


def test_actions_checkout_v7_is_immutably_pinned() -> None:
    offenders = []
    expected = f"actions/checkout@{CHECKOUT_V7_SHA}"
    for path in _workflow_files():
        text = path.read_text(encoding="utf-8")
        if "actions/checkout@v7" in text:
            offenders.append(str(path.relative_to(ROOT)))
        for line in text.splitlines():
            if "actions/checkout@" in line and "# v4" not in line and expected not in line:
                ref = line.split("actions/checkout@", 1)[1].split()[0]
                if ref == "v7":
                    offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
