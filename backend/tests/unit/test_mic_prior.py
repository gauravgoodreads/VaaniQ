"""Unit tests for live-mic decision policy."""

from __future__ import annotations

import numpy as np

from vaaniq.core.types import Label
from vaaniq.streaming.mic_prior import is_live_mic_source, label_from_fake_p


def _pulsed_speech(seconds: float = 2.0, sr: int = 16000) -> np.ndarray:
    t = np.arange(int(sr * seconds), dtype=np.float32) / float(sr)
    gate = (np.sin(2 * np.pi * 3.0 * t) > 0).astype(np.float32)
    tone = np.sin(2 * np.pi * 180.0 * t).astype(np.float32)
    noise = np.random.default_rng(0).normal(0, 0.02, size=t.shape).astype(np.float32)
    return (0.25 * tone * gate) + noise


def test_file_uploads_keep_half_threshold() -> None:
    samples = _pulsed_speech()
    fake, p = label_from_fake_p(0.51, live_mic=False, samples=samples)
    real, _ = label_from_fake_p(0.49, live_mic=False, samples=samples)
    assert fake is Label.FAKE
    assert real is Label.REAL
    assert p == 0.51


def test_live_mic_human_like_speech_is_real_even_if_raw_score_is_high() -> None:
    samples = _pulsed_speech()
    label, _adj = label_from_fake_p(0.9, live_mic=True, samples=samples, sample_rate_hz=16000)
    assert label is Label.REAL


def test_live_mic_still_flags_sure_synthetic() -> None:
    samples = np.sin(2 * np.pi * 220 * np.arange(16000, dtype=np.float32) / 16000).astype(
        np.float32
    )
    label, _adj = label_from_fake_p(0.99, live_mic=True, samples=samples, sample_rate_hz=16000)
    assert label is Label.FAKE


def test_live_source_detection() -> None:
    assert is_live_mic_source("mic", "clip.wav")
    assert is_live_mic_source("file", "vaaniq-recording-1.wav")
    assert is_live_mic_source("file", "live-123.wav")
    assert not is_live_mic_source("file", "hi-fake-2710dee28900583a.flac")
