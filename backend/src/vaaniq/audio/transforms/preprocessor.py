"""Default preprocessor stub (ROADMAP-020 / REQ-098)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.preprocessor import Preprocessor


class DefaultPreprocessor(Preprocessor):
    """Resample, trim, and normalize waveforms.

    TODO(ROADMAP-020): config-driven sample rate, silence trim, peak normalize.
    """

    def transform(self, wav: Waveform) -> Waveform:
        """Preprocess ``wav`` (deferred to ROADMAP-020)."""
        raise NotImplementedInPhaseError("ROADMAP-020", "DefaultPreprocessor.transform")
