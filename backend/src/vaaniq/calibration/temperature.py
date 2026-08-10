"""Temperature scaling calibrator stub (ROADMAP-043 / REQ-054)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.domain.entities import Logits, Probabilities
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.calibrator import Calibrator
from vaaniq.core.types import CompressionCondition, Language


class TemperatureScaler(Calibrator):
    """Per language x condition temperature scaling.

    TODO(ROADMAP-043): fit T on val logits; transform to Probabilities (OQ-031).
    """

    def fit(
        self,
        logits: Sequence[Logits],
        labels: Sequence[int],
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> None:
        """Fit temperature (deferred to ROADMAP-043)."""
        raise NotImplementedInPhaseError("ROADMAP-043", "TemperatureScaler.fit")

    def transform(
        self,
        logits: Logits,
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> Probabilities:
        """Apply temperature (deferred to ROADMAP-043)."""
        raise NotImplementedInPhaseError("ROADMAP-043", "TemperatureScaler.transform")
