"""Canonical detector score contract (REQ-046-053)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

LABEL_REAL: Final[int] = 0
LABEL_FAKE: Final[int] = 1
CLASS_REAL_NAME: Final[str] = "real"
CLASS_FAKE_NAME: Final[str] = "fake"
DEFAULT_DECISION_THRESHOLD: Final[float] = 0.5


@dataclass(frozen=True, slots=True)
class ScoreContract:
    """Documented score semantics shared across VaaniQ."""

    label_real: int = LABEL_REAL
    label_fake: int = LABEL_FAKE
    positive_class: int = LABEL_FAKE
    higher_score_means: str = "higher_probability_of_fake"
    probability_field: str = "score_fake"
    eer_spoof_score_direction: str = "higher_is_more_fake"
    roc_positive_class: int = LABEL_FAKE
    decision_threshold: float = DEFAULT_DECISION_THRESHOLD
    logit_column_order: tuple[str, str] = ("real", "fake")


SCORE_CONTRACT: Final[ScoreContract] = ScoreContract()


def softmax_rows(logits: NDArray[np.floating]) -> NDArray[np.float64]:
    """Row-wise softmax for two-class logits."""
    z = logits - np.max(logits, axis=1, keepdims=True)
    ex = np.exp(z)
    return np.asarray(ex / np.sum(ex, axis=1, keepdims=True), dtype=np.float64)


def logits_to_fake_scores(logits: NDArray[np.floating]) -> NDArray[np.float64]:
    """Convert [real, fake] logits to canonical fake-class scores."""
    probs = softmax_rows(np.asarray(logits, dtype=np.float64))
    if probs.shape[1] < 2:
        msg = f"expected 2-class logits, got shape {probs.shape}"
        raise ValueError(msg)
    return probs[:, SCORE_CONTRACT.positive_class]


def labels_from_strings(raw: object) -> int:
    """Map manifest/API label strings to canonical ints."""
    text = str(raw).lower()
    if text in {CLASS_FAKE_NAME, "spoof", "1"}:
        return LABEL_FAKE
    if text in {CLASS_REAL_NAME, "bonafide", "0"}:
        return LABEL_REAL
    msg = f"unknown label value: {raw!r}"
    raise ValueError(msg)


def score_polarity_audit(
    scores: list[float],
    labels: list[int],
) -> dict[str, float | bool]:
    """Compare metrics on raw vs negated scores to detect polarity bugs."""
    from vaaniq.evaluation.metrics.core import equal_error_rate, roc_curve

    neg = [-float(s) for s in scores]
    _, _, auc_raw = roc_curve(scores, labels)
    _, _, auc_neg = roc_curve(neg, labels)
    eer_raw = equal_error_rate(scores, labels)
    eer_neg = equal_error_rate(neg, labels)
    likely_inverted = auc_raw < 0.5 and auc_neg > 0.5
    return {
        "roc_auc_raw": round(float(auc_raw), 4),
        "roc_auc_negated": round(float(auc_neg), 4),
        "eer_raw": round(float(eer_raw), 4),
        "eer_negated": round(float(eer_neg), 4),
        "likely_score_inversion": likely_inverted,
    }


def mean_scores_by_label(
    scores: list[float],
    labels: list[int],
) -> dict[str, float]:
    """Mean fake-score for real vs fake clips."""
    real = [s for s, y in zip(scores, labels, strict=True) if y == LABEL_REAL]
    fake = [s for s, y in zip(scores, labels, strict=True) if y == LABEL_FAKE]
    return {
        "mean_score_real": round(float(np.mean(real)), 4) if real else 0.0,
        "mean_score_fake": round(float(np.mean(fake)), 4) if fake else 0.0,
    }

