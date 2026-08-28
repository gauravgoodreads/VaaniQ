#!/usr/bin/env python3
"""Research integrity verification — fails on blocking invariant violations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.research.integrity import verify_research_integrity  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_REPO)
    parser.add_argument(
        "--no-require-artifacts",
        action="store_true",
        help="Do not warn when baseline_v1 artifacts are missing.",
    )
    args = parser.parse_args()
    report = verify_research_integrity(
        args.repo_root.resolve(),
        require_baseline_artifacts=not args.no_require_artifacts,
    )
    out = args.repo_root / "artifacts" / "integrity_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if not report.get("ok") else 0


if __name__ == "__main__":
    raise SystemExit(main())
