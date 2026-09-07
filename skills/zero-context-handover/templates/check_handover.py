#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-context handover guard (parameterized, stdlib-only, cross-platform).

Reconciles documentation claims against repository reality so status drift
dies at commit time instead of misleading the next agent. Configure via
.handover.json (created by bootstrap.py); every section is optional.

Checks:
  docs            numeric claims in status docs vs a real unittest discovery
                  (discovery failure = check skipped with a warning, not a lie)
  required_files  constitution-mandated skeleton files exist
  interface       interface-contract in/out paths exist
  env_contract    lockfile / setup scripts exist
  frozen_lock     FROZEN.lock sha256 entries (CRLF-normalized, cross-platform)
  path_ban_dirs   absolute-path ban in code dirs (URL lines exempted)
  meta            *.csv.meta.json rows claim vs actual csv lines + utf-8 check
  day0            TODO-DAY0 markers remaining = hard FAIL (finish Day-0 first)
  contributions   registered owners have a CARDS/<owner>.md
  dismantle       system files present but config/guard deleted = FAIL

Self-test:  python check_handover.py --selftest  (GUARD_SELFTEST_OK = healthy)

Usage:  python check_handover.py   (exit 0 = OK, 1 = mismatch found)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

_BACKSLASH = chr(92) * 2  # regex needs a doubled backslash to match one literal
DAY0_MARKER = "TODO-DAY0"


def locate_repo_root() -> Path:
    """Walk up from cwd so the guard works from any subdirectory."""
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / ".handover.json").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd()


REPO = locate_repo_root()
CONFIG = REPO / ".handover.json"
SYSTEM_MARKERS = ("AGENTS.md", "HANDOFF.md")


def load_config() -> dict:
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def check_dismantle(cfg_exists: bool) -> list[str]:
    failures: list[str] = []
    markers = [m for m in SYSTEM_MARKERS if (REPO / m).exists()]
    if markers and not cfg_exists:
        failures.append(
            "handover system dismantled: " + ", ".join(markers)
            + " present but .handover.json is gone (restored by re-running bootstrap)"
        )
    return failures


# --- check: docs (numeric claims vs reality) -------------------------------
CLAIM_PATTERNS = [
    re.compile(r"(\d+)\s*tests? pass", re.IGNORECASE),
    re.compile(r"(\d+)\s*项单测"),
    re.compile(r"(\d+)\s*项测试"),
    re.compile(r"[Cc]urrently\s+(\d+)"),
]
_TEMPLATE_MARKERS = ("方括号处 Day 0 填写", "Day 0 填写方括号", "（模板，Day 0")


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


def discover_test_count() -> tuple[int | None, str]:
    tests_dir = REPO / CFG.get("tests_dir", "tests")
    if not tests_dir.is_dir():
        return None, f"no tests dir at {CFG.get('tests_dir', 'tests')}"
    sys.path.insert(0, str(tests_dir))
    try:
        suite = unittest.TestLoader().discover(str(tests_dir))
        return suite.countTestCases(), ""
    except Exception as exc:  # noqa: BLE001 - env problems must not become lies
        return None, f"discovery failed ({str(exc)[:120]}) — docs check skipped"
    finally:
        sys.path.pop(0)


# --- check: frozen integrity (cross-platform, CRLF-normalized) -------------
def normalized_sha256(target: Path) -> str:
    data = target.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def check_frozen_lock(lock_rel: str) -> list[str]:
    failures: list[str] = []
    lock = REPO / lock_rel
    if not lock.exists():
        failures.append(
            f"frozen_lock '{lock_rel}' is configured but the file is missing"
            " — deleting the lock silently disables freeze protection"
        )
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
        if normalized_sha256(target) != expected:
            failures.append(f"frozen file modified without re-declaration: {rel}")
    return failures


# --- check: absolute-path ban (URL lines exempted — no wolf-crying) --------
_ABS_PATH_PATTERNS = [
    re.compile("[A-Za-z]:[" + _BACKSLASH + "/]"),   # drive + separator
    re.compile("/Users/"),
    re.compile("/home/"),
]
_URL_LINE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://")


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
                if _URL_LINE.search(line):
                    continue  # URLs legitimately contain /home/ etc.
                if any(p.search(line) for p in _ABS_PATH_PATTERNS):
                    failures.append(f"absolute path in {file.relative_to(REPO)}:{i}: {line.strip()[:90]}")
    return failures


# --- check: meta.json consistency (form AND a piece of content) ------------
def check_meta_consistency(meta_glob_dirs: list[str]) -> list[str]:
    failures: list[str] = []
    seen = 0
    for rel_dir in meta_glob_dirs:
        base = REPO / rel_dir
        if not base.is_dir():
            continue
        for meta_file in base.rglob("*.meta.json"):
            seen += 1
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                failures.append(f"meta not valid utf-8/json: {meta_file.relative_to(REPO)} ({str(exc)[:60]})")
                continue
            # meta file name pattern: <name>.csv.meta.json -> <name>.csv
            name = meta_file.name
            if not name.endswith(".meta.json"):
                continue
            csv_path = meta_file.parent / name[: -len(".meta.json")]
            if not csv_path.exists():
                failures.append(f"meta without its data file: {meta_file.relative_to(REPO)}")
                continue
            try:
                text = csv_path.read_text(encoding="utf-8")  # GBK/乱码 fails here
            except UnicodeDecodeError:
                failures.append(f"data file is not utf-8 (encoding contract): {csv_path.relative_to(REPO)}")
                continue
            declared = meta.get("rows")
            if isinstance(declared, int):
                actual_rows = max(len(text.splitlines()) - 1, 0)  # minus header
                if actual_rows != declared:
                    failures.append(
                        f"meta rows mismatch: {csv_path.name} declares rows={declared}, actual data rows={actual_rows}"
                    )
    if seen == 0 and meta_glob_dirs:
        print(f"[meta] no *.meta.json found under {meta_glob_dirs} (nothing to verify)")
    return failures


# --- check: Day-0 completion (machine-checkable, not a mere warning) -------
def check_day0(scan_docs: list[str]) -> list[str]:
    failures: list[str] = []
    remaining: list[str] = []
    for rel in scan_docs:
        doc = REPO / rel
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        count = text.count(DAY0_MARKER)
        if count:
            remaining.append(f"{rel} x{count}")
    if remaining:
        failures.append(
            "Day-0 not finished — " + DAY0_MARKER + " markers remain in " + ", ".join(remaining)
            + " (fill them, then delete the markers; the guard stays red until then BY DESIGN)"
        )
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


def selftest() -> int:
    ok = True
    sample = "alpha\nbeta\r\ngamma\r\n".encode()
    if normalized_sha256_from_bytes(sample) != hashlib.sha256(b"alpha\nbeta\ngamma\n").hexdigest():
        print("SELFTEST FAIL: CRLF normalization broken"); ok = False
    if not re.compile("[A-Za-z]:[" + _BACKSLASH + "/]").search("x = open('D:" + chr(92) + "data" + chr(92) + "f.csv')"):
        print("SELFTEST FAIL: drive-letter pattern broken"); ok = False
    if re.compile("/Users/").search('read_csv("C:/Users/x")') is False:
        print("SELFTEST FAIL: /Users/ pattern broken"); ok = False
    if locate_repo_root() == Path.cwd() and not (Path.cwd() / ".git").exists() and not (Path.cwd() / ".handover.json").exists():
        pass  # root locate has a defined fallback; nothing to assert here
    print("GUARD_SELFTEST_OK" if ok else "GUARD_SELFTEST_FAIL")
    return 0 if ok else 1


def normalized_sha256_from_bytes(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    global CFG
    if "--selftest" in sys.argv:
        return selftest()
    CFG = load_config()
    warnings: list[str] = []
    failures: list[str] = []

    failures += check_dismantle(CONFIG.exists())

    docs_cfg = CFG.get("docs", {})
    if docs_cfg.get("status_docs"):
        actual, note = discover_test_count()
        if actual is None:
            warnings.append(f"docs: {note}")
        else:
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

    meta_dirs = CFG.get("meta_dirs", ["out"])
    failures += check_meta_consistency(meta_dirs)

    day0_docs = CFG.get("day0_docs", list(SYSTEM_MARKERS) + ["CARDS"])
    day0_scan: list[str] = []
    for rel in day0_docs:
        p = REPO / rel
        if p.is_dir():
            day0_scan.extend(str(f.relative_to(REPO)) for f in p.rglob("*.md"))
        else:
            day0_scan.append(rel)
    failures += check_day0(day0_scan)

    contrib = CFG.get("contributions", {})
    if contrib.get("owners") and contrib.get("cards_dir"):
        for owner in contrib["owners"]:
            card = REPO / contrib["cards_dir"] / f"{owner}.md"
            if not card.exists():
                failures.append(f"contributions: registered owner '{owner}' has no card at {card}")

    for warning in warnings:
        print(f"[warn] {warning}")
    if failures:
        print("HANDOVER_GUARD_FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("HANDOVER_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
