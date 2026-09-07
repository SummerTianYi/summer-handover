#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-context handover guard (parameterized, stdlib-only, cross-platform).

Reconciles documentation claims against repository reality so status drift
dies at commit time instead of misleading the next agent. Configure via
.handover.json (created by bootstrap.py); every section is optional.

Checks:
  docs            numeric claims in status docs vs a real counter function
  required_files  constitution-mandated skeleton files exist
  interface       interface-contract in/out paths exist
  env_contract    lockfile / setup scripts exist
  contributions   registered owners have a CARDS/<owner>.md

Usage:  python check_handover.py   (exit 0 = OK, 1 = mismatch found)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()
CONFIG = REPO / ".handover.json"


def load_config() -> dict:
    if not CONFIG.exists():
        print("[guard] no .handover.json found — nothing to check (scaffold first?)")
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


# --- check: docs (numeric claims vs reality) -------------------------------
CLAIM_PATTERNS = [
    re.compile(r"(\d+)\s*tests? pass", re.IGNORECASE),
    re.compile(r"(\d+)\s*项单测"),
    re.compile(r"(\d+)\s*项测试"),
    re.compile(r"[Cc]urrently\s+(\d+)"),
]


def scan_doc_claims(paths: list[str]) -> list[tuple[str, int, str]]:
    claims: list[tuple[str, int, str]] = []
    for rel in paths:
        doc = REPO / rel
        if not doc.exists():
            continue
        for line in doc.read_text(encoding="utf-8", errors="replace").splitlines():
            for pattern in CLAIM_PATTERNS:
                for match in pattern.finditer(line):
                    claims.append((rel, int(match.group(1)), line.strip()[:100]))
    return claims


def actual_test_count() -> int:
    """Discover unittest cases under the configured tests dir. A project can
    point counter_module at its own counter for non-unittest ecosystems."""
    spec = importlib.util.find_spec  # noqa: F841 - referenced for clarity
    import unittest

    tests_dir = REPO / CFG.get("tests_dir", "tests")
    if not tests_dir.is_dir():
        return 0
    sys.path.insert(0, str(tests_dir))
    try:
        suite = unittest.TestLoader().discover(str(tests_dir))
    finally:
        sys.path.pop(0)
    return suite.countTestCases()


# --- check: frozen integrity (the "don't break finished work" guarantee) ---
# FROZEN.lock lines: <sha256>  <path>  <note>. Declare via scripts/freeze.py
# when the handoff card declares a freeze; guard fails on any drift.
def check_frozen_lock(lock_rel: str) -> list[str]:
    failures: list[str] = []
    lock = REPO / lock_rel
    if not lock.exists():
        return failures
    for line in lock.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) < 2:
            continue
        expected, rel = parts[0], parts[1]
        target = REPO / rel
        if not target.exists():
            failures.append(f"frozen file deleted: {rel}")
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected:
            failures.append(f"frozen file modified without re-declaration: {rel}")
    return failures


# --- check: absolute-path ban (constitution rule, mechanically enforced) ---
_BACKSLASH = chr(92) * 2  # regex needs a doubled backslash to match one literal
_ABS_PATH_PATTERNS = [
    re.compile("[A-Za-z]:[" + _BACKSLASH + "/]"),   # drive + separator
    re.compile("/Users/"),
    re.compile("/home/"),
]


def check_path_ban(scan_dirs: list[str]) -> list[str]:
    failures: list[str] = []
    for rel_dir in scan_dirs:
        base = REPO / rel_dir
        if not base.is_dir():
            continue
        for file in base.rglob("*"):
            if file.suffix.lower() not in (".py", ".sh", ".ps1", ".md", ".json", ".yaml", ".yml", ".toml"):
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if any(p.search(line) for p in _ABS_PATH_PATTERNS):
                    failures.append(f"absolute path in {file.relative_to(REPO)}:{i}: {line.strip()[:90]}")
    return failures


# --- checks: existence-based ----------------------------------------------
def check_existence(rel_paths: list[str], label: str) -> list[str]:
    failures = []
    for rel in rel_paths:
        if not (REPO / rel).exists():
            failures.append(f"{label} missing: {rel}")
    return failures


# --- main ------------------------------------------------------------------
CFG: dict = {}


def main() -> int:
    global CFG
    CFG = load_config()
    failures: list[str] = []

    docs_cfg = CFG.get("docs", {})
    if docs_cfg.get("status_docs"):
        actual = actual_test_count()
        print(f"[docs] actual unittest cases: {actual}")
        for rel, claimed, line in scan_doc_claims(docs_cfg["status_docs"]):
            ok = "ok" if claimed == actual else "MISMATCH"
            print(f"    {rel}: claims {claimed} ({ok})")
            if claimed != actual:
                failures.append(f"{rel} claims {claimed} tests, actual {actual}: {line}")

    failures += check_existence(CFG.get("required_files", []), "required_files")
    failures += check_existence(CFG.get("interface", []), "interface path")
    failures += check_existence(CFG.get("env_contract", []), "env_contract")

    frozen = CFG.get("frozen_lock")
    if frozen:
        failures += check_frozen_lock(frozen)

    path_ban_dirs = CFG.get("path_ban_dirs")
    if path_ban_dirs:
        failures += check_path_ban(path_ban_dirs)

    contrib = CFG.get("contributions", {})
    if contrib.get("owners") and contrib.get("cards_dir"):
        for owner in contrib["owners"]:
            card = REPO / contrib["cards_dir"] / f"{owner}.md"
            if not card.exists():
                failures.append(f"contributions: registered owner '{owner}' has no card at {card}")

    if failures:
        print("HANDOVER_GUARD_FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("HANDOVER_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
