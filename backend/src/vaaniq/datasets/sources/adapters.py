"""Dataset source adapters (stubs; ROADMAP-011)."""

from __future__ import annotations

from collections.abc import Iterator

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.dataset_source import DatasetSourcePort
from vaaniq.core.types import DatasetSource


class KathbathSource(DatasetSourcePort):
    """Kathbath corpus adapter.

    TODO(ROADMAP-011): gated HF access + ClipMetadata yield.
    """

    @property
    def source_id(self) -> DatasetSource:
        """Return Kathbath source id."""
        return DatasetSource.KATHBATH

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Iterate Kathbath clips (deferred to ROADMAP-011)."""
        raise NotImplementedInPhaseError("ROADMAP-011", "KathbathSource.iter_clips")


class IndicVoicesRSource(DatasetSourcePort):
    """IndicVoices-R corpus adapter.

    TODO(ROADMAP-011): gated access + ClipMetadata yield.
    """

    @property
    def source_id(self) -> DatasetSource:
        """Return IndicVoices-R source id."""
        return DatasetSource.INDICVOICES_R

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Iterate IndicVoices-R clips (deferred to ROADMAP-011)."""
        raise NotImplementedInPhaseError("ROADMAP-011", "IndicVoicesRSource.iter_clips")


class CommonVoiceSource(DatasetSourcePort):
    """Mozilla Common Voice adapter (HI/MR; TA via OQ-003).

    TODO(ROADMAP-011): language filters from config.
    """

    @property
    def source_id(self) -> DatasetSource:
        """Return Common Voice source id."""
        return DatasetSource.COMMON_VOICE

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Iterate Common Voice clips (deferred to ROADMAP-011)."""
        raise NotImplementedInPhaseError("ROADMAP-011", "CommonVoiceSource.iter_clips")


class IndicSynthSource(DatasetSourcePort):
    """IndicSynth synthetic fakes adapter.

    TODO(ROADMAP-011 / ROADMAP-014): sample fakes with licence notes.
    """

    @property
    def source_id(self) -> DatasetSource:
        """Return IndicSynth source id."""
        return DatasetSource.INDICSYNTH

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Iterate IndicSynth clips (deferred to ROADMAP-011)."""
        raise NotImplementedInPhaseError("ROADMAP-011", "IndicSynthSource.iter_clips")


class TeamRecordingsSource(DatasetSourcePort):
    """Team-recorded real speech adapter.

    TODO(ROADMAP-011 / ROADMAP-015): consent refs + manifests.
    """

    @property
    def source_id(self) -> DatasetSource:
        """Return team recording source id."""
        return DatasetSource.TEAM_RECORDING

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Iterate team recordings (deferred to ROADMAP-011)."""
        raise NotImplementedInPhaseError("ROADMAP-011", "TeamRecordingsSource.iter_clips")
