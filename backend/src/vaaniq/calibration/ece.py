"""ECE, Brier, entropy, coverage, reliability badge (ROADMAP-044-047).

# ASSUMPTION: OQ-017 - 15 equal-width bins.
# ASSUMPTION: OQ-010 - badge thresholds from config defaults.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from vaaniq.config.domains import ReliabilityBadgeConfig
from vaaniq.core.types import CompressionCondition, ReliabilityLevel

Float64Array = NDArray[np.float64]


def expected_calibration_error(
    confidences: Sequence[float],
    correct: Sequence[int],
    *,
    n_bins: int = 15,
) -> float:
    """Compute Expected Calibration Error (REQ-057).

    Args:
        confidences: Predicted confidence in ``[0, 1]``.
        correct: ``1`` if prediction matched label else ``0``.
        n_bins: Bin count. # ASSUMPTION: OQ-017
    """
    conf = np.asarray(confidences, dtype=np.float64)
    corr = np.asarray(correct, dtype=np.float64)
    if conf.size == 0:
        return 0.0
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (conf >= bins[i]) & (conf < bins[i + 1] if i < n_bins - 1 else conf <= bins[i + 1])
        if not np.any(mask):
            continue
        acc = float(np.mean(corr[mask]))
        avg_conf = float(np.mean(conf[mask]))
        ece += (float(np.sum(mask)) / float(conf.size)) * abs(acc - avg_conf)
    return float(ece)


def reliability_diagram(
    confidences: Sequence[float],
    correct: Sequence[int],
    *,
    n_bins: int = 15,
) -> list[dict[str, float]]:
    """Bin-wise accuracy vs confidence (REQ-058)."""
    conf = np.asarray(confidences, dtype=np.float64)
    corr = np.asarray(correct, dtype=np.float64)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    out: list[dict[str, float]] = []
    for i in range(n_bins):
        lo, hi = float(bins[i]), float(bins[i + 1])
        mask = (conf >= lo) & (conf < hi if i < n_bins - 1 else conf <= hi)
        if not np.any(mask):
            out.append(
                {"bin_lo": lo, "bin_hi": hi, "confidence": 0.0, "accuracy": 0.0, "count": 0.0}
            )
            continue
        out.append(
            {
                "bin_lo": lo,
                "bin_hi": hi,
                "confidence": float(np.mean(conf[mask])),
                "accuracy": float(np.mean(corr[mask])),
                "count": float(np.sum(mask)),
            }
        )
    return out


def brier_score(probabilities: Sequence[float], labels: Sequence[int]) -> float:
    """Brier score for positive-class probabilities (REQ-059)."""
    p = np.asarray(probabilities, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    if p.size == 0:
        return 0.0
    return float(np.mean(np.square(p - y)))


def predictive_entropy(probabilities: Sequence[float]) -> float:
    """Binary entropy of ``[p_real, p_fake]`` or positive-class p (REQ-060)."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.size == 1:
        p = np.array([1.0 - p[0], p[0]], dtype=np.float64)
    p = np.clip(p, 1e-12, 1.0)
    p = p / np.sum(p)
    return float(-np.sum(p * np.log(p)))


def coverage_accuracy_curve(
    confidences: Sequence[float],
    correct: Sequence[int],
    *,
    steps: int = 20,
) -> list[dict[str, float]]:
    """Coverage vs accuracy by confidence threshold (REQ-061)."""
    conf = np.asarray(confidences, dtype=np.float64)
    corr = np.asarray(correct, dtype=np.float64)
    if conf.size == 0:
        return []
    out: list[dict[str, float]] = []
    for thr in np.linspace(0.0, 1.0, steps):
        mask = conf >= thr
        coverage = float(np.mean(mask))
        acc = float(np.mean(corr[mask])) if np.any(mask) else 0.0
        out.append({"threshold": float(thr), "coverage": coverage, "accuracy": acc})
    return out


def reliability_badge(
    confidence: float,
    *,
    entropy: float,
    condition: CompressionCondition,
    config: ReliabilityBadgeConfig | None = None,
) -> ReliabilityLevel:
    """Map confidence/entropy/compression to UI badge (REQ-062).

    # ASSUMPTION: OQ-010
    """
    cfg = config or ReliabilityBadgeConfig()
    # High entropy → LOW
    if entropy >= np.log(2) * 0.9:
        return ReliabilityLevel.LOW
    if cfg.flag_opus_as_moderate and condition == CompressionCondition.OPUS_WHATSAPP_SIM:
        return ReliabilityLevel.MODERATE
    if cfg.moderate_confidence_low <= confidence <= cfg.moderate_confidence_high:
        return ReliabilityLevel.MODERATE
    if confidence < cfg.moderate_confidence_low:
        return ReliabilityLevel.LOW
    return ReliabilityLevel.HIGH
