"""CLI: ``python -m vaaniq.research.cli --mode execute|fixtures``."""

from __future__ import annotations

import argparse
from pathlib import Path

import structlog

from vaaniq.research.execution import execute_research_phase
from vaaniq.research.runner import run_fixture_suites

log = structlog.get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Execute inventory/audit (default) or CI fixture suites."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("execute", "fixtures"), default="execute")
    parser.add_argument("--root", type=Path, default=Path("./research"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    if args.mode == "fixtures":
        payload = run_fixture_suites(args.root, seed=args.seed)
        log.info(
            "research_fixture_suites_written",
            n_reports=len(payload["reports"]),
            root=str(args.root),
            note="fixture_not_rq_result",
        )
        return 0
    summary = execute_research_phase(repo_root=args.repo_root, output_root=args.root)
    log.info(
        "research_execution_complete",
        can_train=summary["audit"]["can_train"],
        n_fixture_clips=summary["n_fixture_clips"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
