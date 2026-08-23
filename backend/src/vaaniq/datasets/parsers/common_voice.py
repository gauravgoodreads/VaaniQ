"""Common Voice row parser (ROADMAP-011 / REQ-103)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource
from vaaniq.datasets.parsers.base import BaseRowParser


class CommonVoiceRowParser(BaseRowParser):
    """Parse Common Voice JSONL/CSV rows into ``ClipMetadata`` (REQ-103).

    Maps ``client_id`` → ``speaker_id`` when the latter is absent.
    """

    source = DatasetSource.COMMON_VOICE

    def normalize(self, row: dict[str, object]) -> dict[str, object]:
        """Apply Common Voice field aliases then shared normalisation."""
        if row.get("speaker_id") is None and "client_id" in row:
            row["speaker_id"] = row.pop("client_id")
        elif "client_id" in row:
            row.pop("client_id")
        return super().normalize(row)
