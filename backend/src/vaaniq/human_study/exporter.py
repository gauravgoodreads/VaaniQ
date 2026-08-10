"""Human-study CSV exporter stub (ROADMAP-059 / REQ-069)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.human_study_exporter import HumanStudyExporter
from vaaniq.core.types import ExportFormat


class CsvHumanStudyExporter(HumanStudyExporter):
    """Export anonymised human-study responses to CSV/JSON.

    TODO(ROADMAP-059): strip PII; honour ExportFormat.
    """

    def export(
        self,
        responses: Sequence[Mapping[str, str]],
        *,
        fmt: ExportFormat,
        destination: Path,
    ) -> Path:
        """Write export (deferred to ROADMAP-059)."""
        raise NotImplementedInPhaseError("ROADMAP-059", "CsvHumanStudyExporter.export")
