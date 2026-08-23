"""Dataset hours/count statistics (ROADMAP-018 / REQ-034)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import Label, Language


@dataclass(frozen=True, slots=True)
class DatasetStatistics:
    """Aggregate hours and counts by language and label (REQ-034).

    Language keys are produced by iterating ``Language`` — never a hardcoded list.
    Serves ROADMAP-018 / OQ-002.
    """

    hours_by_language: Mapping[Language, float]
    counts_by_language: Mapping[Language, int]
    hours_by_label: Mapping[Label, float]
    counts_by_label: Mapping[Label, int]
    total_hours: float
    total_clips: int

    @classmethod
    def compute(cls, clips: Sequence[ClipMetadata]) -> DatasetStatistics:
        """Compute hours and counts from clip metadata.

        Args:
            clips: Curated clip records.

        Returns:
            Frozen statistics with zero-filled language/label buckets.
        """
        hours_by_language = {lang: 0.0 for lang in Language}
        counts_by_language = {lang: 0 for lang in Language}
        hours_by_label = {label: 0.0 for label in Label}
        counts_by_label = {label: 0 for label in Label}
        total_sec = 0.0
        for clip in clips:
            hours_by_language[clip.language] += clip.duration_sec / 3600.0
            counts_by_language[clip.language] += 1
            hours_by_label[clip.label] += clip.duration_sec / 3600.0
            counts_by_label[clip.label] += 1
            total_sec += clip.duration_sec
        return cls(
            hours_by_language=hours_by_language,
            counts_by_language=counts_by_language,
            hours_by_label=hours_by_label,
            counts_by_label=counts_by_label,
            total_hours=total_sec / 3600.0,
            total_clips=len(clips),
        )
