"""Evaluation report generator stub (ROADMAP-041 / REQ-118)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.core.errors import NotImplementedInPhaseError


class EvalReportGenerator:
    """Render evaluation artefacts into a research report.

    TODO(ROADMAP-041): markdown/HTML report from metrics + matrices.
    """

    def write(self, experiment_id: str, destination: Path) -> Path:
        """Write report for ``experiment_id`` (deferred to ROADMAP-041)."""
        raise NotImplementedInPhaseError("ROADMAP-041", "EvalReportGenerator.write")
