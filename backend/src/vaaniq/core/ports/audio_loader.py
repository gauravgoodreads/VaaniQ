"""Audio loading port (REQ-094)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from vaaniq.core.domain.entities import Waveform


class AudioLoader(ABC):
    """Load audio from a URI or path into a waveform.

    Serves REQ-094 (multi-stage decode with fallback). Implementations:
    SoundFileLoader, FallbackDecoderLoader (ROADMAP-019).
    """

    @abstractmethod
    def load(self, uri: str | Path) -> Waveform:
        """Load audio from ``uri``.

        Args:
            uri: Filesystem path or object-store URI.

        Returns:
            Decoded mono waveform.

        Raises:
            AudioDecodeError: If decoding fails.
        """
