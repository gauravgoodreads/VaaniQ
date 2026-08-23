"""Cross-lingual / cross-condition matrices (ROADMAP-038-039)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from vaaniq.core.types import CompressionCondition, Language
from vaaniq.evaluation.metrics.core import equal_error_rate


def cross_lingual_matrix(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float]]:
    """Build train-lang x test-lang EER matrix (REQ-048, REQ-121).

    Args:
        rows: Each mapping needs ``train_lang``, ``test_lang``, ``scores``, ``labels``.

    Returns:
        Nested dict ``matrix[train][test] = eer``.
    """
    matrix: dict[str, dict[str, float]] = {
        lang.value: {other.value: float("nan") for other in Language} for lang in Language
    }
    for row in rows:
        train_lang = str(row["train_lang"])
        test_lang = str(row["test_lang"])
        eer = equal_error_rate(list(row["scores"]), list(row["labels"]))
        matrix.setdefault(train_lang, {})[test_lang] = eer
    return matrix


def cross_condition_matrix(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float]]:
    """Build clean↔Opus condition matrix (REQ-049, REQ-122).

    Args:
        rows: Each mapping needs ``train_condition``, ``test_condition``,
            ``scores``, ``labels``.
    """
    conds = [c.value for c in CompressionCondition]
    matrix: dict[str, dict[str, float]] = {a: {b: float("nan") for b in conds} for a in conds}
    for row in rows:
        a = str(row["train_condition"])
        b = str(row["test_condition"])
        eer = equal_error_rate(list(row["scores"]), list(row["labels"]))
        matrix.setdefault(a, {})[b] = eer
    return matrix


def per_language_report(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, float]]:
    """Per-language EER slice (REQ-080)."""
    from vaaniq.evaluation.metrics.core import classification_report_scores, min_dcf

    out: dict[str, dict[str, float]] = {}
    for row in rows:
        lang = str(row["language"])
        scores = list(row["scores"])
        labels = list(row["labels"])
        out[lang] = {
            "eer": equal_error_rate(scores, labels),
            "min_dcf": min_dcf(scores, labels),
            **classification_report_scores(scores, labels),
        }
    return out


def per_attack_report(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, float]]:
    """Per-attack-type EER slice (REQ-081)."""
    from vaaniq.evaluation.metrics.core import classification_report_scores, min_dcf

    out: dict[str, dict[str, float]] = {}
    for row in rows:
        attack = str(row["attack_type"])
        scores = list(row["scores"])
        labels = list(row["labels"])
        out[attack] = {
            "eer": equal_error_rate(scores, labels),
            "min_dcf": min_dcf(scores, labels),
            **classification_report_scores(scores, labels),
        }
    return out
