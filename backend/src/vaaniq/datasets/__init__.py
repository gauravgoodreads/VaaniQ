"""Dataset package public exports (ROADMAP-011-018)."""

from __future__ import annotations

from vaaniq.datasets.cache.corpus_cache import CorpusCache
from vaaniq.datasets.download.local_cache import LocalCacheDownloader
from vaaniq.datasets.download.manager import DownloadManager
from vaaniq.datasets.download.mock import MockDownloader
from vaaniq.datasets.loaders.manifest_loader import ManifestClipLoader
from vaaniq.datasets.manifests.clip_schema import ClipMetadataModel, parse_clip_metadata
from vaaniq.datasets.normalizers.ids import normalize_clip_id, normalize_speaker_id
from vaaniq.datasets.preview.format import format_preview
from vaaniq.datasets.sources.adapters import (
    CommonVoiceSource,
    GeneratedAudioSource,
    IndicSynthSource,
    IndicVoicesRSource,
    KathbathSource,
    TeamRecordingsSource,
)
from vaaniq.datasets.splits.speaker_disjoint import SpeakerDisjointSplitter
from vaaniq.datasets.stats.statistics import DatasetStatistics
from vaaniq.datasets.validators.gates import language_filter, licence_gate, require_fields

__all__ = [
    "ClipMetadataModel",
    "CommonVoiceSource",
    "CorpusCache",
    "DatasetStatistics",
    "DownloadManager",
    "GeneratedAudioSource",
    "IndicSynthSource",
    "IndicVoicesRSource",
    "KathbathSource",
    "LocalCacheDownloader",
    "ManifestClipLoader",
    "MockDownloader",
    "SpeakerDisjointSplitter",
    "TeamRecordingsSource",
    "format_preview",
    "language_filter",
    "licence_gate",
    "normalize_clip_id",
    "normalize_speaker_id",
    "parse_clip_metadata",
    "require_fields",
]
