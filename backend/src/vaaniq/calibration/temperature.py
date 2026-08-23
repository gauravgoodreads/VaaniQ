"""Temperature scaling calibrator (ROADMAP-043 / REQ-054-056).

# ASSUMPTION: OQ-031 - one temperature per (language x condition).
# ASSUMPTION: OQ-032 - fit on val only.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import structlog
from numpy.typing import NDArray

from vaaniq.core.domain.entities import Logits, Probabilities
from vaaniq.core.errors import CalibrationError
from vaaniq.core.ports.calibrator import Calibrator
from vaaniq.core.types import CompressionCondition, Label, Language

log = structlog.get_logger(__name__)

Float32Array = NDArray[np.float32]


def _softmax_t(logits: Float32Array, temperature: float) -> Float32Array:
    t = max(float(temperature), 1e-6)
    z = logits / t
    z = z - np.max(z, axis=-1, keepdims=True)
    ex = np.exp(z)
    return np.asarray(ex / np.sum(ex, axis=-1, keepdims=True), dtype=np.float32)


class TemperatureScaler(Calibrator):
    """Per-(language, condition) temperature scaling (REQ-054)."""

    def __init__(self) -> None:
        """Initialise empty temperature table."""
        self._temperatures: dict[tuple[str, str], float] = {}

    def fit(
        self,
        logits: Sequence[Logits],
        labels: Sequence[int],
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> None:
        """Fit temperature on held-out validation logits (REQ-055-056)."""
        if len(logits) == 0:
            raise CalibrationError("empty logits for temperature fit")
        if len(logits) != len(labels):
            raise CalibrationError("logits/labels length mismatch")
        stacked = np.stack(
            [np.asarray(item.values, dtype=np.float32) for item in logits],
            axis=0,
        )
        y = np.asarray(labels, dtype=np.int64)
        best_t = 1.0
        best_nll = float("inf")
        # Grid search over T - stable and dependency-free.
        for t in np.linspace(0.5, 5.0, 46):
            probs = _softmax_t(stacked, float(t))
            nll = float(-np.mean(np.log(np.clip(probs[np.arange(len(y)), y], 1e-8, 1.0))))
            if nll < best_nll:
                best_nll = nll
                best_t = float(t)
        key = (language.value, condition.value)
        self._temperatures[key] = best_t
        log.info("temperature_fitted", language=language.value, condition=condition.value, T=best_t)

    def transform(
        self,
        logits: Logits,
        *,
        language: Language,
        condition: CompressionCondition,
    ) -> Probabilities:
        """Apply fitted temperature (default T=1 if unseen cell)."""
        key = (language.value, condition.value)
        t = self._temperatures.get(key, 1.0)
        values = _softmax_t(np.asarray(logits.values, dtype=np.float32), t)
        return Probabilities(
            values=values.astype(np.float32),
            class_order=logits.class_order or (Label.REAL, Label.FAKE),
            temperature=t,
        )

    def get_temperature(self, language: Language, condition: CompressionCondition) -> float:
        """Return fitted T or 1.0."""
        return self._temperatures.get((language.value, condition.value), 1.0)
