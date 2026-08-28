#!/usr/bin/env python3
"""Sync research/results/*.csv from persisted experiment artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
RESULTS = _REPO / "research" / "results"
BACKEND_RESULTS = _REPO / "backend" / "research" / "results"


def _write_csv(path: Path, header: tuple[str, ...], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def _load_metrics(name: str) -> dict[str, object]:
    p = _REPO / "artifacts" / "experiments" / name / "metrics.json"
    if not p.is_file():
        return {}
    raw = json.loads(p.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    baseline = _load_metrics("baseline_v1")
    if not baseline:
        # fall back to train_report
        tr = _REPO / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
        if tr.is_file():
            baseline = json.loads(tr.read_text(encoding="utf-8"))

    header = (
        "status",
        "reason",
        "model",
        "language",
        "condition",
        "eer",
        "min_dcf",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    )

    test_m = baseline.get("test_metrics") or {}
    per_cond = test_m.get("per_condition") or {}
    rq1_rows: list[list[object]] = []
    for condition, metrics in per_cond.items():
        if not isinstance(metrics, dict):
            continue
        rq1_rows.append(
            [
                "COMPLETE",
                "from_baseline_v1_artifacts",
                "acoustic_aasist_v1",
                "all",
                condition,
                metrics.get("eer"),
                metrics.get("min_dcf"),
                metrics.get("accuracy"),
                "",
                "",
                metrics.get("f1"),
                test_m.get("roc_auc"),
            ]
        )
    if rq1_rows:
        for dest in (RESULTS, BACKEND_RESULTS):
            _write_csv(dest / "RQ1_clean_vs_opus.csv", header, rq1_rows)

    rq3 = _load_metrics("rq3_crosslingual")
    rq3_rows: list[list[object]] = []
    for fold_name, fold in (rq3.get("folds") or {}).items():
        if not isinstance(fold, dict):
            continue
        tm = fold.get("test_metrics") or {}
        lang = fold_name.replace("held_out_", "")
        rq3_rows.append(
            [
                "COMPLETE",
                "leave_one_language_out",
                "acoustic_aasist_v1",
                lang,
                "all",
                tm.get("eer"),
                tm.get("min_dcf"),
                tm.get("accuracy"),
                tm.get("precision"),
                tm.get("recall"),
                tm.get("f1"),
                tm.get("roc_auc"),
            ]
        )
    if rq3_rows:
        for dest in (RESULTS, BACKEND_RESULTS):
            _write_csv(dest / "RQ3_cross_lingual_matrix.csv", header, rq3_rows)

    rq4 = _load_metrics("rq4_calibration")
    if rq4:
        rq4_rows = []
        for name, pack in (rq4.get("strategies") or {}).items():
            if isinstance(pack, dict):
                rq4_rows.append(
                    [
                        "COMPLETE",
                        rq4.get("conclusion", ""),
                        "acoustic_aasist_v1",
                        "all",
                        name,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )
        for dest in (RESULTS, BACKEND_RESULTS):
            _write_csv(
                dest / "RQ4_calibration.csv",
                ("status", "note", "model", "language", "strategy", *header[5:]),
                rq4_rows or [["PARTIAL", "run export_predictions.py", "", "", "", "", "", "", "", "", "", ""]],
            )

    for dest in (RESULTS, BACKEND_RESULTS):
        _write_csv(
            dest / "RQ2_multilingual_vs_english.csv",
            header,
            [["PENDING", "ASVspoof English-only control not yet measured (OQ-015)", "", "", "", "", "", "", "", "", "", ""]],
        )
        _write_csv(
            dest / "RQ5_human_vs_model.csv",
            ("status", "reason", "n_participants", "human_accuracy", "model_accuracy"),
            [["PENDING", "human_n=0; protocol ready", 0, "", ""]],
        )

    print("synced research/results CSVs from artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
