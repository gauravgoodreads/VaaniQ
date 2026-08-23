"""Team recordings row parser (ROADMAP-015 / REQ-029 / REQ-074)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource
from vaaniq.datasets.parsers.base import BaseRowParser


class TeamRecordingsRowParser(BaseRowParser):
    """Parse team-recording JSONL/CSV rows into ``ClipMetadata`` (REQ-029)."""

    source = DatasetSource.TEAM_RECORDING
