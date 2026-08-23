"""Human vs model statistics (RQ5 / O6 / OQ-009)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from vaaniq.calibration.ece import brier_score, expected_calibration_error
from vaaniq.evaluation.metrics.core import classification_report_scores


def confidence_1_5_to_prob(value: int) -> float:
    """Map 1-5 slider to ``[0, 1]`` confidence."""
    return (float(value) - 1.0) / 4.0


def mcnemar_b_c(human_correct: Sequence[int], model_correct: Sequence[int]) -> dict[str, int]:
    """McNemar discordant counts (OQ-009). ``b`` = human right/model wrong."""
    b = 0
    c = 0
    for h, m in zip(human_correct, model_correct, strict=True):
        if h == 1 and m == 0:
            b += 1
        if h == 0 and m == 1:
            c += 1
    return {"b": b, "c": c, "n": len(list(human_correct))}


def human_vs_model_report(
    *,
    human_pred: Sequence[int],
    human_conf_1_5: Sequence[int],
    human_labels: Sequence[int],
    model_scores: Sequence[float],
    model_labels: Sequence[int],
) -> dict[str, Any]:
    """Compare human accuracy/confidence/calibration to the model (RQ5)."""
    h_scores = [confidence_1_5_to_prob(v) for v in human_conf_1_5]
    # Treat human pred as fake-class score 0/1 for EER-style accuracy
    h_acc = classification_report_scores(
        [float(p) for p in human_pred],
        list(human_labels),
        threshold=0.5,
    )
    m_acc = classification_report_scores(list(model_scores), list(model_labels), threshold=0.5)
    h_pred_bin = list(human_pred)
    h_correct = [int(p == y) for p, y in zip(h_pred_bin, human_labels, strict=True)]
    m_pred = [1 if s >= 0.5 else 0 for s in model_scores]
    m_correct = [int(p == y) for p, y in zip(m_pred, model_labels, strict=True)]
    h_ece = expected_calibration_error(h_scores, h_correct)
    m_ece = expected_calibration_error(
        [max(s, 1.0 - s) for s in model_scores],
        m_correct,
    )
    return {
        "human_accuracy": h_acc["accuracy"],
        "human_mean_confidence": float(np.mean(h_scores)) if h_scores else 0.0,
        "human_ece": h_ece,
        "human_brier": brier_score(h_scores, list(human_labels)),
        "model_accuracy": m_acc["accuracy"],
        "model_ece": m_ece,
        "model_brier": brier_score(list(model_scores), list(model_labels)),
        "mcnemar": mcnemar_b_c(h_correct, m_correct),
    }
