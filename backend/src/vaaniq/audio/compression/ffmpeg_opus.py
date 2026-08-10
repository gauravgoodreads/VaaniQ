"""FFmpeg Opus compressor stub (ROADMAP-021 / REQ-113)."""

from __future__ import annotations

from collections.abc import Mapping

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.compressor import Compressor


class FFmpegOpusCompressor(Compressor):
    """WhatsApp-style Opus compression via ffmpeg.

    TODO(ROADMAP-021): honour configs/audio/compression.yaml (OQ-007).
    """

    def compress(self, wav: Waveform, cfg: Mapping[str, str]) -> Waveform:
        """Compress ``wav`` (deferred to ROADMAP-021)."""
        raise NotImplementedInPhaseError("ROADMAP-021", "FFmpegOpusCompressor.compress")
