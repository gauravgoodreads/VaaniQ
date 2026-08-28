"""Tests for research integrity, artifacts, and diagnostics."""

from __future__ import annotations

from pathlib import Path

import pytest

from vaaniq.research.artifacts import sync_baseline_v1_from_train_report
from vaaniq.research.calibration_audit import run_calibration_audit
from vaaniq.research.integrity import verify_research_integrity
from vaaniq.research.split_diagnostics import (
    build_final_analysis,
    diagnose_validation_test_gap,
)


def test_calibration_audit_strategies() -> None:
    import numpy as np

    rng = np.random.default_rng(0)
    val_logits = rng.normal(0, 1, size=(40, 2)).astype(np.float32)
    test_logits = rng.normal(0, 1, size=(40, 2)).astype(np.float32)
    val_labels = (rng.random(40) > 0.5).astype(np.int64)
    test_labels = (rng.random(40) > 0.5).astype(np.int64)
    langs = np.array(["hi"] * 40)
    conds = np.array(["clean"] * 40)
    out = run_calibration_audit(
        val_logits,
        val_labels,
        test_logits,
        test_labels,
        langs,
        conds,
        langs,
        conds,
    )
    assert "strategies" in out
    assert "uncalibrated" in out["strategies"]
    assert "ece" in out["strategies"]["uncalibrated"]


def test_integrity_verification_on_repo(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[3]
    report_path = root / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    if not report_path.is_file():
        pytest.skip("train_report.json not present locally")
    sync_baseline_v1_from_train_report(root)
    report = verify_research_integrity(root)
    assert "ok" in report
    assert report.get("n_manifest_clips", 0) >= 0


def test_split_diagnostics(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[3]
    manifest = root / "data" / "publication_corpus" / "manifest.jsonl"
    if not manifest.is_file():
        pytest.skip("publication corpus not present locally")
    diag = diagnose_validation_test_gap(root)
    assert "val_profile" in diag
    assert "test_profile" in diag
    assert "train_profile" in diag
    assert "duration_sec" in diag["val_profile"]
    assert isinstance(diag.get("hypotheses"), list)

    final_analysis = build_final_analysis(root)
    assert "splits" in final_analysis
    assert "score_distributions" in final_analysis
    assert "train" in final_analysis["splits"]
