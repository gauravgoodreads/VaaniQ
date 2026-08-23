"""Generated (Parler-TTS / XTTS) row parser (ROADMAP-016 / REQ-105-106)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource, Label
from vaaniq.datasets.parsers.base import BaseRowParser


class GeneratedAudioRowParser(BaseRowParser):
    """Parse generated-audio rows; default source is Parler-TTS (REQ-105).

    Rows may override ``source`` to ``xtts_v2`` (REQ-106).
    """

    source = DatasetSource.PARLER_TTS

    def normalize(self, row: dict[str, object]) -> dict[str, object]:
        """Default label to fake when omitted."""
        if "label" not in row:
            row["label"] = Label.FAKE.value
        return super().normalize(row)
