"""Kathbath row parser (ROADMAP-011 / REQ-101)."""

from __future__ import annotations

from vaaniq.core.types import DatasetSource
from vaaniq.datasets.parsers.base import BaseRowParser


class KathbathRowParser(BaseRowParser):
    """Parse Kathbath JSONL/CSV rows into ``ClipMetadata`` (REQ-101)."""

    source = DatasetSource.KATHBATH
