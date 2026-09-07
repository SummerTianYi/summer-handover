#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Declare a file as frozen: record its sha256 in FROZEN.lock + audit trail.

Usage (repo root):  python scripts/freeze.py <file> [note]

Every re-declaration is APPENDED to FROZEN.history.log (timestamp + file +
new hash + note), so a sneaky freeze can never erase what it replaced.
Hashes are CRLF-normalized (cross-platform safe).
"""
from __future__ import annotations
import datetime
import hashlib
import sys
from pathlib import Path

LOCK_HEADER = "# frozen files - hash over CRLF-normalized content; edit only via scripts/freeze.py after a handoff-card declaration\n"
HISTORY_HEADER = "# freeze audit trail (append-only)\n"


def normalized_sha256(target: Path) -> str:
    data = target.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: freeze.py <file> [note]")
        return 1
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"not found: {target}")
        return 1
    note = sys.argv[2] if len(sys.argv) > 2 else ""
    digest = normalized_sha256(target)
    rel = target.as_posix()
    stamp = datetime.datetime.now().replace(microsecond=0).isoformat()

    lock = Path("FROZEN.lock")
    kept = []
    if lock.exists():
        for line in lock.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 2)
            if len(parts) > 1 and parts[1] == rel:
                continue  # re-declaration replaces the live entry
            kept.append(line)
    kept.append(f"{digest}  {rel}  {note}".rstrip())
    lock.write_text(LOCK_HEADER + "\n".join(kept) + "\n", encoding="utf-8")

    history = Path("FROZEN.history.log")
    if not history.exists():
        history.write_text(HISTORY_HEADER, encoding="utf-8")
    with history.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}  {digest}  {rel}  {note}\n")

    print(f"frozen: {rel} ({digest[:12]}...)  [audit -> {history.as_posix()}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
