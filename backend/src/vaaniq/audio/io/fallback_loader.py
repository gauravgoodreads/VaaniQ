"""Fallback audio decoder stub (ROADMAP-019 / REQ-094)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.audio_loader import AudioLoader


class FallbackDecoderLoader(AudioLoader):
    """Secondary decoder (ffmpeg/torchaudio) when primary decode fails.

    TODO(ROADMAP-019): chain after SoundFileLoader on AudioDecodeError.
    """

    def load(self, uri: str | Path) -> Waveform:
        """Load audio from ``uri`` (deferred to ROADMAP-019)."""
        raise NotImplementedInPhaseError("ROADMAP-019", "FallbackDecoderLoader.load")
