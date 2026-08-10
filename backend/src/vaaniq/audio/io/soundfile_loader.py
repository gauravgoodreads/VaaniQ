"""SoundFile-based audio loader stub (ROADMAP-019 / REQ-094)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.audio_loader import AudioLoader


class SoundFileLoader(AudioLoader):
    """Primary decoder via soundfile/libsndfile.

    TODO(ROADMAP-019): implement multi-format decode with mono conversion.
    """

    def load(self, uri: str | Path) -> Waveform:
        """Load audio from ``uri`` (deferred to ROADMAP-019)."""
        raise NotImplementedInPhaseError("ROADMAP-019", "SoundFileLoader.load")
