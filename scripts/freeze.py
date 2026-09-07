#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Declare a file as frozen: append its sha256 to FROZEN.lock.

Usage (repo root):  python /path/to/scripts/freeze.py src/brin/clean.py "v1 frozen"
"""
from __future__ import annotations
import hashlib, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: freeze.py <file> [note]")
        return 1
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"not found: {target}")
        return 1
    note = sys.argv[2] if len(sys.argv) > 2 else ""
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    rel = target.as_posix()
    lock = Path("FROZEN.lock")
    kept = []
    if lock.exists():
        for line in lock.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 2)
            if len(parts) > 1 and parts[1] == rel:
                continue  # re-declaration replaces the old entry
            kept.append(line)
    kept.append(f"{digest}  {rel}  {note}".rstrip())
    lock.write_text(
        "# frozen files — modify only via scripts/freeze.py after handoff-card declaration\n"
        + "\n".join(kept) + "\n",
        encoding="utf-8",
    )
    print(f"frozen: {rel} ({digest[:12]}...)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
