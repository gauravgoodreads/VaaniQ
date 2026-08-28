"""Unit tests for canonical score contract."""

from __future__ import annotations

import numpy as np

from vaaniq.evaluation.score_contract import (
    LABEL_FAKE,
    LABEL_REAL,
    SCORE_CONTRACT,
    labels_from_strings,
    logits_to_fake_scores,
    score_polarity_audit,
)


def test_label_mapping() -> None:
    assert labels_from_strings("real") == LABEL_REAL
    assert labels_from_strings("fake") == LABEL_FAKE
    assert labels_from_strings("bonafide") == LABEL_REAL
    assert labels_from_strings("spoof") == LABEL_FAKE


def test_logits_to_fake_scores_higher_for_fake_class() -> None:
    logits = np.array([[2.0, -2.0], [-2.0, 2.0]], dtype=np.float64)
    scores = logits_to_fake_scores(logits)
    assert scores[0] < SCORE_CONTRACT.decision_threshold
    assert scores[1] > SCORE_CONTRACT.decision_threshold


def test_polarity_audit_detects_inversion() -> None:
    labels = [0, 0, 1, 1]
    good = [0.1, 0.2, 0.8, 0.9]
    bad = [0.9, 0.8, 0.2, 0.1]
    assert score_polarity_audit(good, labels)["likely_score_inversion"] is False
    assert score_polarity_audit(bad, labels)["likely_score_inversion"] is True
