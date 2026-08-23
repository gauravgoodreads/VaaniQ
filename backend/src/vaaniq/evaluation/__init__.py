"""Evaluation package public exports."""

from __future__ import annotations

from vaaniq.evaluation.matrices.core import (
    cross_condition_matrix,
    cross_lingual_matrix,
    per_attack_report,
    per_language_report,
)
from vaaniq.evaluation.metrics.core import (
    bootstrap_metric_ci,
    classification_report_scores,
    confusion_matrix,
    equal_error_rate,
    min_dcf,
    pr_curve,
    roc_curve,
)
from vaaniq.evaluation.reports.generator import EvalReportGenerator

__all__ = [
    "EvalReportGenerator",
    "bootstrap_metric_ci",
    "classification_report_scores",
    "confusion_matrix",
    "cross_condition_matrix",
    "cross_lingual_matrix",
    "equal_error_rate",
    "min_dcf",
    "per_attack_report",
    "per_language_report",
    "pr_curve",
    "roc_curve",
]
