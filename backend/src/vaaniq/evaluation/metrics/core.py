"""Evaluation metric stubs (ROADMAP-036+ / REQ-046-053)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.errors import NotImplementedInPhaseError


def equal_error_rate(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Compute EER (deferred to ROADMAP-036)."""
    raise NotImplementedInPhaseError("ROADMAP-036", "equal_error_rate")


def min_dcf(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Compute min-DCF (deferred to ROADMAP-036)."""
    raise NotImplementedInPhaseError("ROADMAP-036", "min_dcf")


def classification_report_scores(
    scores: Sequence[float],
    labels: Sequence[int],
) -> dict[str, float]:
    """Accuracy / P / R / F1 (deferred to ROADMAP-037)."""
    raise NotImplementedInPhaseError("ROADMAP-037", "classification_report_scores")
