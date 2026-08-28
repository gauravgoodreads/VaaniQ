"""Load persisted experiment artifacts for document generation."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO / "artifacts" / "experiments"


def load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def load_experiment(name: str) -> dict[str, object]:
    return load_json(ARTIFACTS / name / "metrics.json")


def load_train_report() -> dict[str, object]:
    primary = REPO / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    if primary.is_file():
        return load_json(primary)
    return load_experiment("baseline_v1")


def load_xlsr_main() -> dict[str, object]:
    report = REPO / "models" / "checkpoints" / "xlsr_main" / "train_report.json"
    if report.is_file():
        return load_json(report)
    return load_experiment("xlsr_main")


def load_baseline_matrix() -> dict[str, object]:
    return load_experiment("baseline_matrix")


def load_rq2() -> dict[str, object]:
    return load_experiment("rq2_english_control")


def load_rq4_audit() -> dict[str, object]:
    return load_experiment("rq4_calibration")


def load_benchmark_v2() -> dict[str, object]:
    return load_experiment("benchmark_v2")


def load_source_shortcut() -> dict[str, object]:
    return load_experiment("source_shortcut")
