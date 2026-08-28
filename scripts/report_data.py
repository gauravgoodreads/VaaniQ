"""Load persisted experiment artifacts for document generation."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO / "artifacts" / "experiments"
FINAL_MANIFEST = REPO / "artifacts" / "final_results_manifest.json"


def load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def load_experiment(name: str) -> dict[str, object]:
    return load_json(ARTIFACTS / name / "metrics.json")


def load_final_results() -> dict[str, object]:
    """Load the frozen Round 3 results manifest."""
    return load_json(FINAL_MANIFEST)


def load_train_report() -> dict[str, object]:
    """Load Baseline V1 metadata with frozen metrics overriding legacy values."""
    primary = REPO / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    report = load_json(primary) if primary.is_file() else {}
    baseline = load_final_results().get("baseline_v1")
    if not isinstance(baseline, dict):
        return report or load_experiment("baseline_v1")
    canonical = dict(report)
    metrics = baseline.get("metrics")
    validation = baseline.get("validation_metrics")
    if isinstance(metrics, dict):
        canonical["test_metrics"] = metrics
        canonical["eval_metrics"] = metrics
        canonical["n_test"] = metrics.get("n", canonical.get("n_test", 0))
        for source, target in (
            ("accuracy", "test_accuracy"),
            ("eer", "test_eer"),
            ("min_dcf", "test_min_dcf"),
            ("roc_auc", "test_roc_auc"),
            ("ece", "test_ece"),
            ("brier", "test_brier"),
        ):
            canonical[target] = metrics.get(source)
    if isinstance(validation, dict):
        canonical["validation_metrics"] = validation
    canonical["canonical_source"] = str(FINAL_MANIFEST)
    canonical["approved_commit"] = "084bd47ca6ca1b69a7cdbf424e2946f3794c2a95"
    return canonical


def load_xlsr_main() -> dict[str, object]:
    """Load the frozen XLS-R result from the Round 3 manifest."""
    result = load_final_results().get("xlsr_main")
    if isinstance(result, dict):
        return result
    report = REPO / "models" / "checkpoints" / "xlsr_main" / "train_report.json"
    if report.is_file():
        return load_json(report)
    return load_experiment("xlsr_main")


def load_baseline_matrix() -> dict[str, object]:
    return load_experiment("baseline_matrix")


def load_rq2() -> dict[str, object]:
    frozen = load_final_results().get("rq2")
    if isinstance(frozen, dict) and frozen:
        return frozen
    return load_experiment("rq2_english_control")


def load_rq4_audit() -> dict[str, object]:
    frozen = load_final_results().get("rq4")
    if isinstance(frozen, dict) and frozen:
        return frozen
    return load_experiment("rq4_calibration")


def load_benchmark_v2() -> dict[str, object]:
    frozen = load_final_results().get("benchmark_v2")
    if isinstance(frozen, dict) and frozen:
        return frozen
    return load_experiment("benchmark_v2")


def load_source_shortcut() -> dict[str, object]:
    return load_experiment("source_shortcut")


def as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def as_number(mapping: dict[str, object], key: str, default: float = 0.0) -> float:
    value = mapping.get(key, default)
    return float(value) if isinstance(value, int | float) else default


def pct(value: float, digits: int = 2) -> str:
    """Format a proportion as a percentage, e.g. 0.9161 -> 91.61%."""
    return f"{value * 100:.{digits}f}%"
