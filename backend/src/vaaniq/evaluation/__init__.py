"""Evaluation package public exports (Phase 1 stubs)."""

from __future__ import annotations

from vaaniq.evaluation.matrices.core import cross_condition_matrix, cross_lingual_matrix
from vaaniq.evaluation.metrics.core import (
    classification_report_scores,
    equal_error_rate,
    min_dcf,
)
from vaaniq.evaluation.reports.generator import EvalReportGenerator

__all__ = [
    "EvalReportGenerator",
    "classification_report_scores",
    "cross_condition_matrix",
    "cross_lingual_matrix",
    "equal_error_rate",
    "min_dcf",
]
