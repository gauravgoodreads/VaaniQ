"""Audio preprocessing port (REQ-098)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vaaniq.core.domain.entities import Waveform


class Preprocessor(ABC):
    """Resample, trim silence, and normalize waveforms.

    Serves REQ-098. Implementation: FFmpegPreprocessor / torchaudio path
    (ROADMAP-020).
    """

    @abstractmethod
    def transform(self, wav: Waveform) -> Waveform:
        """Return a preprocessed waveform.

        Args:
            wav: Input waveform.

        Returns:
            Transformed waveform at the configured sample rate.
        """
