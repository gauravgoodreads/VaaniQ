#!/usr/bin/env python3
"""Fail if Telugu appears as a project language code.

REQ-139 / ROADMAP-001. Allows prose that forbids Telugu or notes tool coverage,
but rejects Language enums/configs that adopt ``te`` / Telugu as a project language.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths scanned for hard language-code defects
SCAN_GLOBS = (
    "backend/**/*.py",
    "frontend/src/**/*.ts",
    "frontend/src/**/*.tsx",
    "configs/**/*.yaml",
    "configs/**/*.yml",
)

# Explicit project-language assignment patterns that must never use Telugu
FORBIDDEN = [
    re.compile(r'\bLanguage\.[Tt][Ee]\b'),
    re.compile(r'["\']te["\']\s*[:=]'),
    re.compile(r'language\s*[:=]\s*["\']te["\']', re.I),
    re.compile(r'\bTELUGU\b'),
    re.compile(r'\bTelugu\b'),
    re.compile(r'\btelugu\b'),
]


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted({p for p in files if p.is_file()})


def main() -> int:
    """Return 0 if clean, 1 if a forbidden project-language usage is found."""
    hits: list[str] = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            # Allow comments/docs that forbid Telugu
            # Allow lines that forbid / assert absence of Telugu (REQ-139 tests, rules).
            if re.search(
                r"\b(no|not|never|forbid|forbids|defect|banned|must not)\b"
                r"|REQ-139|NOT in this project",
                line,
                re.I,
            ) and re.search(r"telugu|\bte\b", line, re.I):
                continue
            for pat in FORBIDDEN:
                if pat.search(line):
                    rel = path.relative_to(ROOT).as_posix()
                    hits.append(f"{rel}:{i}: {line.strip()}")
                    break
    if hits:
        print("REQ-139 violation: Telugu must not be a project language:", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
