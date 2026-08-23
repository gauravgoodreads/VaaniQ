"""Evaluation report generator (ROADMAP-041 / REQ-118)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class EvalReportGenerator:
    """Write markdown + JSON evaluation reports."""

    def write(
        self,
        experiment_id: str,
        destination: Path,
        *,
        metrics: dict[str, Any] | None = None,
        matrices: dict[str, Any] | None = None,
        slices: dict[str, Any] | None = None,
    ) -> Path:
        """Write report for ``experiment_id``.

        Args:
            experiment_id: Run id.
            destination: Output markdown path.
            metrics: Scalar metrics.
            matrices: Cross matrices.
            slices: Per-language / per-attack slices.

        Returns:
            Path to written markdown report.
        """
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        metrics = metrics or {}
        matrices = matrices or {}
        slices = slices or {}
        lines = [
            f"# Evaluation report - `{experiment_id}`",
            "",
            "## Metrics",
            "```json",
            json.dumps(metrics, indent=2),
            "```",
            "",
            "## Matrices",
            "```json",
            json.dumps(matrices, indent=2),
            "```",
            "",
            "## Slices",
            "```json",
            json.dumps(slices, indent=2),
            "```",
            "",
        ]
        destination.write_text("\n".join(lines), encoding="utf-8")
        json_path = destination.with_suffix(".json")
        json_path.write_text(
            json.dumps(
                {
                    "experiment_id": experiment_id,
                    "metrics": metrics,
                    "matrices": matrices,
                    "slices": slices,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        log.info("eval_report_written", path=str(destination))
        return destination
