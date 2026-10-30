"""Data-independent tests for research integrity rules."""

from __future__ import annotations

import json
from pathlib import Path

from vaaniq.research.integrity import (
    verify_document_claims,
    verify_research_integrity,
    verify_train_report_integrity,
)


def _clean_report() -> dict[str, object]:
    return {
        "n_train": 70,
        "n_val": 15,
        "n_test": 15,
        "n_clips": 100,
        "speaker_disjoint_verified": True,
        "pipeline": "preprocess -> acoustic embedding -> AASIST head",
        "front_end": "acoustic_embedding_1024d",
        "model_name": "acoustic_aasist_v1",
        "test_metrics": {"calibration_pre": {"ece": 0.05}, "calibration_post": {"ece": 0.03}},
    }


def test_clean_report_has_no_issues() -> None:
    assert verify_train_report_integrity(_clean_report()) == []


def test_split_sum_mismatch_flagged() -> None:
    report = _clean_report() | {"n_clips": 120}
    issues = verify_train_report_integrity(report)
    assert any(i.startswith("split_sum_mismatch") for i in issues)


def test_missing_speaker_disjoint_flagged() -> None:
    report = _clean_report() | {"speaker_disjoint_verified": False}
    assert "speaker_disjoint_verified_false_or_missing" in verify_train_report_integrity(report)


def test_calibration_worsening_reported_honestly() -> None:
    report = _clean_report() | {
        "validation_metrics": {
            "calibration_pre": {"ece": 0.02},
            "calibration_post": {"ece": 0.04},
        }
    }
    issues = verify_train_report_integrity(report)
    assert any(i.startswith("calibration_worsened_on_val") for i in issues)


def test_acoustic_pipeline_named_xlsr_flagged() -> None:
    report = _clean_report() | {"model_name": "xlsr_aasist"}
    assert "pipeline_is_acoustic_but_model_name_implies_xlsr" in verify_train_report_integrity(
        report
    )


def test_document_overclaims_detected(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "Calibration improved everywhere. Human study complete with N = 24.",
        encoding="utf-8",
    )
    warnings = verify_document_claims(tmp_path)
    assert "README.md:calibration_improved_unqualified" in warnings
    assert "README.md:human_study_complete_n0" in warnings


def test_document_claims_clean_repo(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Bounded V1 results only.", encoding="utf-8")
    assert verify_document_claims(tmp_path) == []


def test_empty_repo_is_ok_with_warnings(tmp_path: Path) -> None:
    result = verify_research_integrity(tmp_path)
    assert result["ok"] is True
    assert "train_report_missing" in result["warnings"]
    assert result["n_manifest_clips"] == 0


def test_inconsistent_train_report_blocks(tmp_path: Path) -> None:
    ckpt = tmp_path / "models" / "checkpoints" / "xlsr_aasist"
    ckpt.mkdir(parents=True)
    bad = _clean_report() | {"speaker_disjoint_verified": False}
    (ckpt / "train_report.json").write_text(json.dumps(bad), encoding="utf-8")
    result = verify_research_integrity(tmp_path)
    assert result["ok"] is False
    assert "speaker_disjoint_verified_false_or_missing" in result["blocking"]
