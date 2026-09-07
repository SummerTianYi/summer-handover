#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bootstrap the zero-context handover system into the current repository.

Copies templates, writes a .handover.json config, scaffolds the environment
contract, and prints the Day-0 checklist. Stdlib only; safe to re-run (never
overwrites existing files).

Usage (from the target repo root):
  python /path/to/summer-handover/scripts/bootstrap.py --preset sprint \
      --owners alice,brin,cary
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "zero-context-handover"
TEMPLATES = SKILL / "templates"

PRESETS = {
    "sprint": {"docs": False},
    "standard": {"docs": True},
    "full": {"docs": True},
}

DEFAULT_SKELETON = ["data", "src", "out/figures", "out/tables", "docs", "tests", "CARDS"]

GITIGNORE = """__pycache__/
*.pyc
.venv/
out/spool/
"""

SETUP_SH = """#!/usr/bin/env bash
# environment contract entry point (edit me: real deps on Day 0)
set -e
python3 -m pip install -r "$(dirname "$0")/requirements.lock"
echo "env ready"
"""

SETUP_PS1 = """# environment contract entry point (edit me: real deps on Day 0)
python -m pip install -r "$PSScriptRoot/requirements.lock"
Write-Host "env ready"
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=sorted(PRESETS), default="sprint")
    parser.add_argument("--owners", default="", help="comma-separated owner names")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    repo = Path.cwd()
    if not (repo / ".git").exists():
        print("[bootstrap] WARNING: current dir is not a git repo (continue anyway)")

    created: list[str] = []
    skipped: list[str] = []

    def place(target: Path, source: Path | None, content: str | None = None) -> None:
        if target.exists() and not args.force:
            skipped.append(str(target))
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if source is not None:
            shutil.copyfile(source, target)
        else:
            target.write_text(content, encoding="utf-8")
        created.append(str(target))

    for target, source in {
        "AGENTS.md": TEMPLATES / "AGENTS.md",
        "HANDOFF.md": TEMPLATES / "HANDOFF.md",
        "CONTRIBUTIONS.md": TEMPLATES / "CONTRIBUTIONS.md",
        "check_handover.py": TEMPLATES / "check_handover.py",
    }.items():
        place(repo / target, source)

    # freeze helper lives IN the target repo (FROZEN.lock header names it)
    place(repo / "scripts" / "freeze.py", Path(__file__).resolve().parent / "freeze.py")

    # environment contract scaffolds (owner fills real deps on Day 0)
    owners = [o.strip() for o in args.owners.split(",") if o.strip()]
    place(repo / "requirements.lock", None, "# pin exact versions on Day 0\n")
    place(repo / "setup.sh", None, SETUP_SH)
    place(repo / "setup.ps1", None, SETUP_PS1)
    place(repo / "data" / "MANIFEST.md", None, "# 原始数据清单：文件 / 大小 / sha256 / 来源\n")
    place(repo / ".gitignore", None, GITIGNORE)

    for owner in owners:
        place(repo / "CARDS" / f"{owner}.md", TEMPLATES / "CARDS_owner.md")

    for rel in DEFAULT_SKELETON:
        (repo / rel).mkdir(parents=True, exist_ok=True)
    if not (repo / "out" / "MANIFEST.md").exists():
        (repo / "out" / "MANIFEST.md").write_text("# 生成物清单\n", encoding="utf-8")

    config = {
        "preset": args.preset,
        "required_files": ["AGENTS.md", "HANDOFF.md", "CONTRIBUTIONS.md"],
        "interface": ["data", "out"],
        "env_contract": ["requirements.lock", "setup.sh", "setup.ps1", "data/MANIFEST.md"],
        "path_ban_dirs": ["src"],
        "frozen_lock": "FROZEN.lock",
        "contributions": {"owners": owners, "cards_dir": "CARDS"},
    }
    if PRESETS[args.preset]["docs"]:
        config["docs"] = {"status_docs": ["HANDOFF.md", "README.md"]}
    cfg_path = repo / ".handover.json"
    if cfg_path.exists() and not args.force:
        skipped.append(".handover.json")
    else:
        cfg_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        created.append(".handover.json")

    print(f"[bootstrap] preset={args.preset}")
    print(f"  created: {created}")
    print(f"  skipped (already existed): {skipped}")
    print("\nDay-0 checklist:")
    print("  1. Fill AGENTS.md skeleton/interface contract (delete template hints)")
    print("  2. Fill HANDOFF.md north star + territory board (one row per owner)")
    print("  3. Everyone registers in CONTRIBUTIONS.md; write your first CARDS/<owner>.md")
    print("  4. Pin real deps in requirements.lock; fill data/MANIFEST.md")
    print("  5. Freeze finished artifacts: python scripts/freeze.py <file> \"note\"")
    print("  6. Run: python check_handover.py  (must be green before every commit)")
    print("  7. Add templates/ci-snippet.yml as .github/workflows/handover.yml (matrix x3 OS)")
    print("  8. Commit all with message suffix (handover-init)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
