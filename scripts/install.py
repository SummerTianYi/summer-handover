#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install the zero-context-handover skill into the local agent skill dirs.

Works for any agent that reads a skills folder. Auto-detects common skill
directories, copies the skill there, and verifies. Stdlib only.

Usage:  python install.py            (auto-detect + install)
        python install.py --dir X    (install into X/zero-context-handover)
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "skills" / "zero-context-handover"
HOME = Path.home()
CANDIDATES = [
    HOME / ".agents" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".codex" / "skills",
    HOME / ".config" / "agents" / "skills",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="", help="explicit skills directory")
    args = parser.parse_args()

    if args.dir:
        targets = [Path(args.dir).expanduser()]
    else:
        targets = [d for d in CANDIDATES if d.parent.exists()] or [CANDIDATES[0]]

    installed = []
    for skills_dir in targets:
        dest = skills_dir / "zero-context-handover"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SRC, dest)
        installed.append(str(dest))

    print("installed:")
    for d in installed:
        print(f"  {d}")
    print("\nverify: the folder contains SKILL.md + templates/ ;")
    print("your agent now understands: \"给这个仓库装零上下文交接系统\" / \"set up handover for this repo\"")
    print("(agents without skill discovery can simply read SKILL.md and follow it)")
    print("assemble into a repo: python <skill_dir>/scripts/bootstrap.py --preset sprint --owners a,b,c")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
