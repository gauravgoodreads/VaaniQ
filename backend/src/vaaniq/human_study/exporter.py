"""Human-study CSV/JSON exporter (ROADMAP-059 / REQ-069)."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from vaaniq.core.ports.human_study_exporter import HumanStudyExporter
from vaaniq.core.types import ExportFormat

_FORBIDDEN = frozenset({"name", "email", "phone", "address"})


def _strip_pii(row: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k, v in row.items() if k.lower() not in _FORBIDDEN}


class CsvHumanStudyExporter(HumanStudyExporter):
    """Export anonymised human-study responses to CSV or JSON."""

    def export(
        self,
        responses: Sequence[Mapping[str, str]],
        *,
        fmt: ExportFormat,
        destination: Path,
    ) -> Path:
        """Write anonymised ``responses`` to ``destination``."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        cleaned = [_strip_pii(row) for row in responses]
        if fmt == ExportFormat.JSON:
            destination.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
            return destination
        fieldnames: list[str] = []
        for row in cleaned:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
        with destination.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames or ["participant_id"])
            writer.writeheader()
            writer.writerows(cleaned)
        return destination
