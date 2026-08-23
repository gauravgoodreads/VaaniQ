"""Research package: experiment store, RQ suites, reports, figures."""

from __future__ import annotations

from vaaniq.research.calibration_study import run_calibration_suite
from vaaniq.research.compression_study import (
    apply_condition,
    condition_catalog,
    run_compression_suite,
)
from vaaniq.research.cross_lingual import leave_one_language_folds, run_cross_lingual_suite
from vaaniq.research.error_analysis import analyze_errors
from vaaniq.research.execution import execute_research_phase
from vaaniq.research.figures import (
    write_confusion_svg,
    write_csv,
    write_heatmap_svg,
    write_line_svg,
    write_roc_svg,
)
from vaaniq.research.publication import write_publication_bundle
from vaaniq.research.records import ResearchRunRecord
from vaaniq.research.reports import ResearchReportBundle
from vaaniq.research.runner import run_fixture_suites
from vaaniq.research.store import ExperimentStore, collect_hardware

__all__ = [
    "ExperimentStore",
    "ResearchReportBundle",
    "ResearchRunRecord",
    "analyze_errors",
    "apply_condition",
    "collect_hardware",
    "condition_catalog",
    "execute_research_phase",
    "leave_one_language_folds",
    "run_calibration_suite",
    "run_compression_suite",
    "run_cross_lingual_suite",
    "run_fixture_suites",
    "write_confusion_svg",
    "write_csv",
    "write_heatmap_svg",
    "write_line_svg",
    "write_publication_bundle",
    "write_roc_svg",
]
