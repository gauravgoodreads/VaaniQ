"""IndicSynth row parser (ROADMAP-011 / ROADMAP-014 / REQ-104)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource, Label
from vaaniq.datasets.parsers.base import BaseRowParser


class IndicSynthRowParser(BaseRowParser):
    """Parse IndicSynth JSONL/CSV rows into ``ClipMetadata`` (REQ-104)."""

    source = DatasetSource.INDICSYNTH

    def normalize(self, row: dict[str, object]) -> dict[str, object]:
        """Default label to fake when omitted."""
        if "label" not in row:
            row["label"] = Label.FAKE.value
        return super().normalize(row)
