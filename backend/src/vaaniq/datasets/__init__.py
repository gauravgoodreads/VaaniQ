"""Dataset package public exports (Phase 1 stubs)."""

from __future__ import annotations

from vaaniq.datasets.manifests.clip_schema import parse_clip_metadata
from vaaniq.datasets.sources.adapters import (
    CommonVoiceSource,
    IndicSynthSource,
    IndicVoicesRSource,
    KathbathSource,
    TeamRecordingsSource,
)
from vaaniq.datasets.splits.speaker_disjoint import SpeakerDisjointSplitter

__all__ = [
    "CommonVoiceSource",
    "IndicSynthSource",
    "IndicVoicesRSource",
    "KathbathSource",
    "SpeakerDisjointSplitter",
    "TeamRecordingsSource",
    "parse_clip_metadata",
]
