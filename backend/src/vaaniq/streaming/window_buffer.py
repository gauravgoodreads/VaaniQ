"""Streaming window buffer (ROADMAP-055 / REQ-096).

# Live windows: 3.0 s / 1.0 s hop (more stable than 2.0/0.5 for mic speech).
"""

from __future__ import annotations

import struct
from collections.abc import Iterator

import numpy as np

from vaaniq.core.domain.entities import Waveform


class WindowBuffer:
    """PCM byte buffer that emits fixed-duration sliding windows."""

    def __init__(
        self,
        *,
        sample_rate_hz: int = 16000,
        window_sec: float = 3.0,
        hop_sec: float = 1.0,
        sample_width_bytes: int = 2,
    ) -> None:
        """Configure window/hop.

        # ASSUMPTION: OQ-019
        """
        self.sample_rate_hz = sample_rate_hz
        self.window_samples = int(window_sec * sample_rate_hz)
        self.hop_samples = int(hop_sec * sample_rate_hz)
        self.sample_width_bytes = sample_width_bytes
        self._pcm = bytearray()
        self._emitted = 0

    def push(self, chunk: bytes) -> list[Waveform]:
        """Ingest PCM bytes and return any completed windows."""
        self._pcm.extend(chunk)
        out: list[Waveform] = []
        bytes_per = self.sample_width_bytes
        total_samples = len(self._pcm) // bytes_per
        while self._emitted + self.window_samples <= total_samples:
            start = self._emitted * bytes_per
            end = (self._emitted + self.window_samples) * bytes_per
            frame = bytes(self._pcm[start:end])
            samples = self._pcm16_to_float(frame)
            out.append(Waveform(samples=samples, sample_rate_hz=self.sample_rate_hz))
            self._emitted += self.hop_samples
        # Trim consumed prefix occasionally
        keep_from = max(0, self._emitted - self.window_samples) * bytes_per
        if keep_from > 0:
            self._pcm = self._pcm[keep_from:]
            self._emitted -= keep_from // bytes_per
        return out

    def reset(self) -> None:
        """Clear buffer state."""
        self._pcm.clear()
        self._emitted = 0

    def iter_windows(self) -> Iterator[Waveform]:
        """Yield nothing; windows are produced via ``push``."""
        return iter(())

    @staticmethod
    def _pcm16_to_float(frame: bytes) -> np.ndarray:
        n = len(frame) // 2
        ints = struct.unpack("<" + "h" * n, frame)
        return (np.asarray(ints, dtype=np.float32) / 32768.0).astype(np.float32)
