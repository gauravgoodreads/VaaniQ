"""Reference tests for min-DCF (REQ-047 / OQ-018).

Hand-computed toy cases verify ASVspoof-style defaults:
``P_target=0.05``, ``C_miss=1.0``, ``C_fa=1.0``, normalised by
``min(C_miss * P_target, C_fa * (1 - P_target))``.
"""

from __future__ import annotations

import pytest

from vaaniq.evaluation.metrics.core import min_dcf

# ASVspoof 2019 LA evaluation defaults (OQ-018).
_P_TARGET = 0.05
_C_MISS = 1.0
_C_FA = 1.0
_NORM_DENOM = min(_C_MISS * _P_TARGET, _C_FA * (1.0 - _P_TARGET))


def _hand_min_dcf(
    scores: list[float],
    labels: list[int],
    *,
    p_target: float = _P_TARGET,
    c_miss: float = _C_MISS,
    c_fa: float = _C_FA,
) -> float:
    """Brute-force min-DCF mirroring ``metrics.core.min_dcf``."""
    best = float("inf")
    thresholds = sorted(set(scores))
    n_real = sum(1 for lab in labels if lab == 0)
    n_fake = sum(1 for lab in labels if lab == 1)
    for threshold in thresholds:
        fpr = sum(
            1
            for score, lab in zip(scores, labels, strict=True)
            if score >= threshold and lab == 0
        )
        fnr = sum(
            1
            for score, lab in zip(scores, labels, strict=True)
            if score < threshold and lab == 1
        )
        fpr_rate = fpr / n_real if n_real else 0.0
        fnr_rate = fnr / n_fake if n_fake else 0.0
        dcf = c_miss * fnr_rate * p_target + c_fa * fpr_rate * (1.0 - p_target)
        best = min(best, dcf)
    denom = min(c_miss * p_target, c_fa * (1.0 - p_target))
    return best / denom if denom > 0 else best


def test_min_dcf_asvspoof_defaults_perfect_separation() -> None:
    """Perfect ranking yields normalised min-DCF of zero."""
    scores = [0.10, 0.40, 0.50, 0.60, 0.70, 0.90]
    labels = [0, 0, 0, 1, 1, 1]
    expected = _hand_min_dcf(scores, labels)
    assert expected == pytest.approx(0.0)
    assert min_dcf(scores, labels) == pytest.approx(expected)
    assert min_dcf(
        scores,
        labels,
        p_target=_P_TARGET,
        c_miss=_C_MISS,
        c_fa=_C_FA,
    ) == pytest.approx(expected)


def test_min_dcf_asvspoof_defaults_overlapping_scores() -> None:
    """Hand-computed overlapping case at threshold ``0.65``.

    Real scores ``0.55, 0.60, 0.65`` vs fake ``0.40, 0.45, 0.50``:
    at ``t=0.65`` → FPR ``1/3``, FNR ``1`` → raw DCF ``0.366667`` → norm ``7.333333``.
    """
    scores = [0.55, 0.60, 0.65, 0.40, 0.45, 0.50]
    labels = [0, 0, 0, 1, 1, 1]
    # Hand derivation documented in docstring above.
    raw_dcf = _C_MISS * 1.0 * _P_TARGET + _C_FA * (1.0 / 3.0) * (1.0 - _P_TARGET)
    expected = raw_dcf / _NORM_DENOM
    assert expected == pytest.approx(7.333333333333333)
    assert _hand_min_dcf(scores, labels) == pytest.approx(expected)
    assert min_dcf(scores, labels) == pytest.approx(expected)


def test_min_dcf_normalisation_denominator() -> None:
    """Normalisation uses ``min(C_miss*P_target, C_fa*(1-P_target))``."""
    assert pytest.approx(0.05) == _NORM_DENOM
