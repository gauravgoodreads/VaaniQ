#!/usr/bin/env python3
"""Sync persisted experiment artifacts from on-disk training outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.research.artifacts import (  # noqa: E402
    sync_baseline_v1_from_train_report,
    sync_rq3_from_checkpoints,
)
from vaaniq.research.split_diagnostics import write_split_diagnostics_artifacts  # noqa: E402
from vaaniq.research.source_shortcut import run_source_shortcut_analysis  # noqa: E402


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_REPO)
    args = parser.parse_args()
    repo = args.repo_root.resolve()

    summary: dict[str, object] = {}
    summary["baseline_v1"] = sync_baseline_v1_from_train_report(repo)
    summary["rq3"] = sync_rq3_from_checkpoints(repo)

    diag_paths = write_split_diagnostics_artifacts(repo)
    summary["split_diagnostics"] = diag_paths

    try:
        shortcut = run_source_shortcut_analysis(repo)
        sdest = repo / "artifacts" / "experiments" / "source_shortcut"
        sdest.mkdir(parents=True, exist_ok=True)
        _write_json(sdest / "metrics.json", shortcut)
        summary["source_shortcut"] = shortcut
    except FileNotFoundError as exc:
        summary["source_shortcut"] = {"skipped": str(exc)}

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
