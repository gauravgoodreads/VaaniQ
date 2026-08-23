"""Evaluation metrics (ROADMAP-036-037 / REQ-046-053).

# ASSUMPTION: OQ-018 - min-DCF uses ASVspoof-style defaults
(P_target=0.05, C_miss=1.0, C_fa=1.0).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

Float64Array = NDArray[np.float64]


def _as_arrays(
    scores: Sequence[float],
    labels: Sequence[int],
) -> tuple[Float64Array, Float64Array]:
    return (
        np.asarray(scores, dtype=np.float64),
        np.asarray(labels, dtype=np.float64),
    )


def _class_conditional_rates(
    pred_fake: NDArray[np.bool_],
    y: Float64Array,
) -> tuple[float, float]:
    """Return FPR = P(fake|real) and FNR = P(real|fake)."""
    n_real = float(np.sum(y == 0))
    n_fake = float(np.sum(y == 1))
    fpr = float(np.sum(pred_fake & (y == 0)) / n_real) if n_real > 0 else 0.0
    fnr = float(np.sum((~pred_fake) & (y == 1)) / n_fake) if n_fake > 0 else 0.0
    return fpr, fnr


def equal_error_rate(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Compute Equal Error Rate (REQ-046).

    Args:
        scores: Higher = more fake (positive class).
        labels: ``1`` = fake, ``0`` = real.

    Returns:
        EER in ``[0, 1]`` using class-conditional FPR/FNR (ASVspoof-style).
    """
    s, y = _as_arrays(scores, labels)
    if s.size == 0:
        return 1.0
    thresholds = np.unique(s)
    if thresholds.size == 0:
        return 1.0
    best = 1.0
    for t in thresholds:
        pred_fake = s >= t
        fpr, fnr = _class_conditional_rates(pred_fake, y)
        best = min(best, max(fpr, fnr))
    return float(best)


def min_dcf(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    p_target: float = 0.05,
    c_miss: float = 1.0,
    c_fa: float = 1.0,
) -> float:
    """Compute minimum detection cost function (REQ-047).

    # ASSUMPTION: OQ-018 - ASVspoof defaults for costs / prior.
    """
    s, y = _as_arrays(scores, labels)
    if s.size == 0:
        return 1.0
    thresholds = np.unique(s)
    best = float("inf")
    for t in thresholds:
        pred_fake = s >= t
        fpr, fnr = _class_conditional_rates(pred_fake, y)
        dcf = c_miss * fnr * p_target + c_fa * fpr * (1.0 - p_target)
        best = min(best, dcf)
    # Normalise by min(c_miss*p_target, c_fa*(1-p_target))
    denom = min(c_miss * p_target, c_fa * (1.0 - p_target))
    return float(best / denom) if denom > 0 else float(best)


def classification_report_scores(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    threshold: float = 0.5,
) -> dict[str, float]:
    """Accuracy / precision / recall / F1 at a fixed threshold (REQ-050)."""
    s, y = _as_arrays(scores, labels)
    if s.size == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
    pred = (s >= threshold).astype(np.float64)
    tp = float(np.sum((pred == 1) & (y == 1)))
    tn = float(np.sum((pred == 0) & (y == 0)))
    fp = float(np.sum((pred == 1) & (y == 0)))
    fn = float(np.sum((pred == 0) & (y == 1)))
    acc = (tp + tn) / float(s.size)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def roc_curve(
    scores: Sequence[float],
    labels: Sequence[int],
) -> tuple[list[float], list[float], float]:
    """Return FPR, TPR lists and AUC (REQ-051)."""
    s, y = _as_arrays(scores, labels)
    if s.size == 0:
        return [0.0, 1.0], [0.0, 1.0], 0.5
    order = np.argsort(-s)
    y_sorted = y[order]
    tps = np.cumsum(y_sorted == 1)
    fps = np.cumsum(y_sorted == 0)
    p = max(float(np.sum(y == 1)), 1.0)
    n = max(float(np.sum(y == 0)), 1.0)
    tpr = (tps / p).tolist()
    fpr = (fps / n).tolist()
    tpr = [0.0, *tpr]
    fpr = [0.0, *fpr]
    auc = float(np.trapezoid(np.asarray(tpr, dtype=np.float64), np.asarray(fpr, dtype=np.float64)))
    return fpr, tpr, abs(auc)


def pr_curve(
    scores: Sequence[float],
    labels: Sequence[int],
) -> tuple[list[float], list[float]]:
    """Precision-recall curve points."""
    s, y = _as_arrays(scores, labels)
    if s.size == 0:
        return [0.0], [0.0]
    thresholds = np.unique(s)
    precision: list[float] = []
    recall: list[float] = []
    for t in thresholds:
        pred = s >= t
        tp = float(np.sum(pred & (y == 1)))
        fp = float(np.sum(pred & (y == 0)))
        fn = float(np.sum((~pred) & (y == 1)))
        precision.append(tp / (tp + fp) if (tp + fp) > 0 else 0.0)
        recall.append(tp / (tp + fn) if (tp + fn) > 0 else 0.0)
    return precision, recall


def confusion_matrix(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    threshold: float = 0.5,
) -> list[list[int]]:
    """2x2 confusion [[TN, FP], [FN, TP]] (REQ-052)."""
    s, y = _as_arrays(scores, labels)
    pred = (s >= threshold).astype(np.float64)
    tn = int(np.sum((pred == 0) & (y == 0)))
    fp = int(np.sum((pred == 1) & (y == 0)))
    fn = int(np.sum((pred == 0) & (y == 1)))
    tp = int(np.sum((pred == 1) & (y == 1)))
    return [[tn, fp], [fn, tp]]


def bootstrap_metric_ci(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    metric: str = "eer",
    n_samples: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Bootstrap CI for EER or min-DCF (ROADMAP-042 / OQ-009).

    Args:
        scores: Fake-class scores.
        labels: Binary labels.
        metric: ``eer`` or ``min_dcf``.
        n_samples: Resample count. # ASSUMPTION: OQ-009
        ci_level: Interval level. # ASSUMPTION: OQ-009
        seed: RNG seed.

    Returns:
        ``(point, lo, hi)``.
    """
    s, y = _as_arrays(scores, labels)
    fn = equal_error_rate if metric == "eer" else min_dcf
    point = fn(s.tolist(), y.astype(int).tolist())
    if s.size == 0:
        return point, point, point
    rng = np.random.default_rng(seed)
    stats: list[float] = []
    n = int(s.size)
    for _ in range(max(1, n_samples)):
        idx = rng.integers(0, n, size=n)
        stats.append(fn(s[idx].tolist(), y[idx].astype(int).tolist()))
    alpha = (1.0 - ci_level) / 2.0
    lo = float(np.quantile(stats, alpha))
    hi = float(np.quantile(stats, 1.0 - alpha))
    return float(point), lo, hi
