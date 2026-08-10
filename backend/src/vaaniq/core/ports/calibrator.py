"""Calibration port (REQ-054)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from vaaniq.core.domain.entities import Logits, Probabilities
from vaaniq.core.types import CompressionCondition, Language


class Calibrator(ABC):
    """Post-hoc probability calibration.

    Serves REQ-054-056 (temperature scaling per language x condition).
    Implementation: TemperatureScaler (ROADMAP-043).
    """

    @abstractmethod
    def fit(
        self,
        logits: Sequence[Logits],
        labels: Sequence[int],
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> None:
        """Fit calibration parameters on a held-out validation split.

        Args:
            logits: Model logits.
            labels: Integer class indices aligned with ``logits``.
            language: Language cell being calibrated.
            condition: Compression condition cell.
        """

    @abstractmethod
    def transform(
        self,
        logits: Logits,
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> Probabilities:
        """Apply fitted calibration to ``logits``.

        Args:
            logits: Raw logits.
            language: Language cell.
            condition: Compression condition cell.

        Returns:
            Calibrated probabilities.
        """
