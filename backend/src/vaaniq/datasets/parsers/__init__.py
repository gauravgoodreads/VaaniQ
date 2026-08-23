"""Per-source manifest row parsers (ROADMAP-011 / ROADMAP-012)."""

from __future__ import annotations

from vaaniq.datasets.parsers.base import BaseRowParser
from vaaniq.datasets.parsers.common_voice import CommonVoiceRowParser
from vaaniq.datasets.parsers.generated_audio import GeneratedAudioRowParser
from vaaniq.datasets.parsers.indicsynth import IndicSynthRowParser
from vaaniq.datasets.parsers.indicvoices_r import IndicVoicesRRowParser
from vaaniq.datasets.parsers.kathbath import KathbathRowParser
from vaaniq.datasets.parsers.team_recordings import TeamRecordingsRowParser

__all__ = [
    "BaseRowParser",
    "CommonVoiceRowParser",
    "GeneratedAudioRowParser",
    "IndicSynthRowParser",
    "IndicVoicesRRowParser",
    "KathbathRowParser",
    "TeamRecordingsRowParser",
]
