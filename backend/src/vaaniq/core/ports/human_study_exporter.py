"""Human-study export port (REQ-069)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path

from vaaniq.core.types import ExportFormat


class HumanStudyExporter(ABC):
    """Export anonymised human-study responses.

    Serves REQ-069, REQ-073. Implementation: CsvExporter (ROADMAP-059).
    """

    @abstractmethod
    def export(
        self,
        responses: Sequence[Mapping[str, str]],
        *,
        fmt: ExportFormat,
        destination: Path,
    ) -> Path:
        """Write ``responses`` to ``destination`` in ``fmt``.

        Args:
            responses: Anonymised row dicts (no PII).
            fmt: Export format.
            destination: Output path.

        Returns:
            Path written.
        """
