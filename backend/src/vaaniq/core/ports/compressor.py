"""Compression port for WhatsApp-style Opus twins (REQ-113)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from vaaniq.core.domain.entities import Waveform


class Compressor(ABC):
    """Produce Opus-compressed twins of clean audio.

    Serves REQ-018, REQ-113 (ffmpeg Opus; OQ-007 for exact args).
    Implementation: FFmpegOpusCompressor (ROADMAP-021).
    """

    @abstractmethod
    def compress(self, wav: Waveform, cfg: Mapping[str, str]) -> Waveform:
        """Compress ``wav`` according to ``cfg``.

        Args:
            wav: Clean waveform.
            cfg: Codec parameters from configs/audio/compression.yaml.

        Returns:
            Compressed waveform (decoded back to PCM for training/eval).
        """
