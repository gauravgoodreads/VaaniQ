"""IndicVoices-R row parser (ROADMAP-011 / REQ-102)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource
from vaaniq.datasets.parsers.base import BaseRowParser


class IndicVoicesRRowParser(BaseRowParser):
    """Parse IndicVoices-R JSONL/CSV rows into ``ClipMetadata`` (REQ-102)."""

    source = DatasetSource.INDICVOICES_R
