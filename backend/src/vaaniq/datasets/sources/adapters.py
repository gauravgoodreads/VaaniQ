"""Dataset source adapters with offline manifest/row mode (ROADMAP-011)."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import DatasetError
from vaaniq.core.ports.dataset_source import DatasetSourcePort
from vaaniq.core.types import DatasetSource
from vaaniq.datasets.loaders.manifest_loader import ManifestClipLoader
from vaaniq.datasets.parsers.base import BaseRowParser
from vaaniq.datasets.parsers.common_voice import CommonVoiceRowParser
from vaaniq.datasets.parsers.generated_audio import GeneratedAudioRowParser
from vaaniq.datasets.parsers.indicsynth import IndicSynthRowParser
from vaaniq.datasets.parsers.indicvoices_r import IndicVoicesRRowParser
from vaaniq.datasets.parsers.kathbath import KathbathRowParser
from vaaniq.datasets.parsers.team_recordings import TeamRecordingsRowParser


class _OfflineSource(DatasetSourcePort):
    """Shared offline iterator over ``manifest_path`` or in-memory ``rows``.

    Network downloads are intentionally out of the default path used by tests
    (ROADMAP-011 / REQ-130).
    """

    _parser: BaseRowParser

    def __init__(
        self,
        *,
        manifest_path: Path | None = None,
        rows: Sequence[Mapping[str, object]] | None = None,
    ) -> None:
        """Bind offline inputs.

        Args:
            manifest_path: Local JSONL/JSON manifest (canonical schema).
            rows: In-memory raw rows parsed via the source-specific parser.
        """
        self._manifest_path = manifest_path
        self._rows = rows

    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Yield clips from rows or a local manifest.

        Yields:
            Validated ``ClipMetadata`` records.

        Raises:
            DatasetError: If neither offline input is provided.
        """
        if self._rows is not None:
            for row in self._rows:
                yield self._parser.parse(row)
            return
        if self._manifest_path is not None:
            yield from ManifestClipLoader().iter_clips(self._manifest_path)
            return
        msg = (
            f"{type(self).__name__}: offline mode requires manifest_path or rows "
            "(network download is not the default test path)"
        )
        raise DatasetError(msg)


class KathbathSource(_OfflineSource):
    """Kathbath corpus adapter (REQ-101 / ROADMAP-011)."""

    _parser = KathbathRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return Kathbath source id."""
        return DatasetSource.KATHBATH


class IndicVoicesRSource(_OfflineSource):
    """IndicVoices-R corpus adapter (REQ-102 / ROADMAP-011)."""

    _parser = IndicVoicesRRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return IndicVoices-R source id."""
        return DatasetSource.INDICVOICES_R


class CommonVoiceSource(_OfflineSource):
    """Mozilla Common Voice adapter (REQ-103 / ROADMAP-011; TA via OQ-003)."""

    _parser = CommonVoiceRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return Common Voice source id."""
        return DatasetSource.COMMON_VOICE


class IndicSynthSource(_OfflineSource):
    """IndicSynth synthetic fakes adapter (REQ-104 / ROADMAP-011 / ROADMAP-014)."""

    _parser = IndicSynthRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return IndicSynth source id."""
        return DatasetSource.INDICSYNTH


class TeamRecordingsSource(_OfflineSource):
    """Team-recorded real speech adapter (REQ-029 / ROADMAP-015)."""

    _parser = TeamRecordingsRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return team recording source id."""
        return DatasetSource.TEAM_RECORDING


class GeneratedAudioSource(_OfflineSource):
    """Parler-TTS / XTTS generated fakes adapter (REQ-105-106 / ROADMAP-016).

    ``source_id`` defaults to ``PARLER_TTS``; individual rows may set ``xtts_v2``.
    """

    _parser = GeneratedAudioRowParser()

    @property
    def source_id(self) -> DatasetSource:
        """Return default generated-audio source id (Parler-TTS)."""
        return DatasetSource.PARLER_TTS
