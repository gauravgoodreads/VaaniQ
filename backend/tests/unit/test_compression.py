"""Compression engine tests (ROADMAP-021); skips when ffmpeg missing/unusable."""

from __future__ import annotations

import shutil
import subprocess

import numpy as np
import pytest

from vaaniq.audio.compression.ffmpeg_opus import CompressionError, FFmpegOpusCompressor
from vaaniq.config.domains import AudioCompressionConfig
from vaaniq.core.domain.entities import Waveform


def _ffmpeg_usable() -> bool:
    """Return True when ffmpeg is on PATH and can be executed.

    Windows Application Control (WDAC) may leave the binary on PATH but block
    spawn; treat that as unavailable so unit tests skip instead of fail.
    """
    bin_path = shutil.which("ffmpeg")
    if bin_path is None:
        return False
    try:
        proc = subprocess.run(
            [bin_path, "-version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


pytestmark = pytest.mark.skipif(
    not _ffmpeg_usable(),
    reason="ffmpeg not on PATH or blocked by OS policy",
)


def _sine(seconds: float = 0.6) -> Waveform:
    sr = 16000
    n = int(sr * seconds)
    t = np.arange(n, dtype=np.float32) / np.float32(sr)
    return Waveform(
        samples=(0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32), sample_rate_hz=sr
    )


def test_opus_compress_with_metadata() -> None:
    comp = FFmpegOpusCompressor(AudioCompressionConfig())
    out, meta = comp.compress_with_metadata(_sine(), parent_clip_id="clip-1")
    assert out.samples.size > 0
    assert meta.bitrate_kbps == 16
    assert meta.pair_id.startswith("pair_")
    assert meta.child_clip_id.startswith("clip-1")


def test_compress_port_mapping() -> None:
    comp = FFmpegOpusCompressor()
    out = comp.compress(_sine(), {"bitrate_kbps": "16"})
    assert out.sample_rate_hz == 16000


def test_missing_ffmpeg_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("vaaniq.audio.compression.ffmpeg_opus.shutil.which", lambda _x: None)
    with pytest.raises(CompressionError):
        FFmpegOpusCompressor().compress(_sine(), {})
