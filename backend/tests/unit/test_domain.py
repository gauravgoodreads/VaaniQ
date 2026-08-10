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
