"""Tests for domain entities (ROADMAP-003)."""

from __future__ import annotations

import numpy as np

from vaaniq.core.domain import ClipMetadata, Waveform
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    Split,
)


def test_waveform_duration() -> None:
    """Duration is samples / sample_rate."""
    samples = np.zeros(16000, dtype=np.float32)
    wav = Waveform(samples=samples, sample_rate_hz=16000)
    assert wav.duration_sec == 1.0


def test_waveform_zero_rate_duration() -> None:
    """Invalid sample rate yields zero duration."""
    samples = np.zeros(10, dtype=np.float32)
    wav = Waveform(samples=samples, sample_rate_hz=0)
    assert wav.duration_sec == 0.0


def test_clip_metadata_requires_language_enum() -> None:
    """ClipMetadata stores Language enum, not free strings (REQ-131-133)."""
    meta = ClipMetadata(
        clip_id="clip-001",
        language=Language.HI,
        source=DatasetSource.COMMON_VOICE,
        label=Label.REAL,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=16000,
        duration_sec=2.5,
        split=Split.TRAIN,
        dataset_source="mozilla-foundation/common_voice_17_0",
        speaker_id=None,
    )
    assert meta.language is Language.HI
    assert meta.attack_type is None
    # ASSUMPTION: OQ-036 — optional enrichment defaults
    assert meta.gender is None
    assert meta.file_size_bytes is None
    assert meta.speaker_age is None
    assert meta.emotion is None
    assert meta.recording_medium is None
    assert meta.quality is None
    assert meta.checksum_sha256 is None
    assert meta.uri is None


def test_clip_metadata_optional_enrichment() -> None:
    """Optional enrichment fields can be set (ASSUMPTION: OQ-036)."""
    meta = ClipMetadata(
        clip_id="clip-002",
        language=Language.TA,
        source=DatasetSource.PARLER_TTS,
        label=Label.FAKE,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=16000,
        duration_sec=1.0,
        split=Split.VAL,
        dataset_source="local/generated",
        gender="f",
        file_size_bytes=2048,
        uri="/data/clip-002.wav",
        checksum_sha256="deadbeef",
    )
    assert meta.gender == "f"
    assert meta.file_size_bytes == 2048
    assert meta.uri == "/data/clip-002.wav"
