"""Validation vs test gap diagnostics (P7).

Investigates heterogeneous validation subsets without altering splits.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import Split
from vaaniq.datasets.loaders.manifest_loader import ManifestClipLoader


def _load_rows(manifest_path: Path) -> list[ClipMetadata]:
    loader = ManifestClipLoader()
    return list(loader.iter_clips(manifest_path))


def _duration_stats(durations: list[float]) -> dict[str, float | None]:
    """Summarise clip durations in seconds."""
    if not durations:
        return {
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
            "median": None,
            "p25": None,
            "p75": None,
            "total_sec": None,
        }
    arr = np.asarray(durations, dtype=np.float64)
    return {
        "mean": round(float(np.mean(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "total_sec": round(float(np.sum(arr)), 4),
    }


def _speaker_counter(clips: list[ClipMetadata]) -> Counter[str]:
    return Counter(c.speaker_id or c.clip_id for c in clips)


def _split_profile(clips: list[ClipMetadata], split: Split) -> dict[str, Any]:
    subset = [c for c in clips if c.split == split]
    speakers = _speaker_counter(subset)
    langs = Counter(c.language.value for c in subset)
    labels = Counter(c.label.value for c in subset)
    sources = Counter(c.source.value for c in subset)
    conditions = Counter(c.compression_status.value for c in subset)
    durations = [c.duration_sec for c in subset if c.duration_sec is not None]

    speakers_by_lang: dict[str, int] = {}
    for lang in ("hi", "mr", "ta"):
        lang_clips = [c for c in subset if c.language.value == lang]
        speakers_by_lang[lang] = len(_speaker_counter(lang_clips))

    cross_lang_label: dict[str, dict[str, int]] = defaultdict(dict)
    for lang in ("hi", "mr", "ta"):
        for label in ("real", "fake"):
            n = sum(
                1
                for c in subset
                if c.language.value == lang and c.label.value == label
            )
            cross_lang_label[lang][label] = n

    cross_source_label: dict[str, dict[str, int]] = defaultdict(dict)
    for source in sorted({c.source.value for c in subset}):
        for label in ("real", "fake"):
            n = sum(
                1
                for c in subset
                if c.source.value == source and c.label.value == label
            )
            cross_source_label[source][label] = n

    return {
        "n": len(subset),
        "n_speakers": len(speakers),
        "speakers_per_language": speakers_by_lang,
        "languages": dict(langs),
        "labels": dict(labels),
        "sources": dict(sources),
        "conditions": dict(conditions),
        "lang_x_label": {k: dict(v) for k, v in cross_lang_label.items()},
        "source_x_label": {k: dict(v) for k, v in cross_source_label.items()},
        "duration_sec": _duration_stats(durations),
    }


def _score_distribution_bins(
    scores: list[float], *, n_bins: int = 10
) -> list[dict[str, float | int]]:
    if not scores:
        return []
    arr = np.asarray(scores, dtype=np.float64)
    counts, edges = np.histogram(arr, bins=n_bins, range=(0.0, 1.0))
    bins: list[dict[str, float | int]] = []
    for idx, count in enumerate(counts.tolist()):
        lo = float(edges[idx])
        hi = float(edges[idx + 1])
        bins.append(
            {
                "bin_lo": round(lo, 4),
                "bin_hi": round(hi, 4),
                "count": int(count),
            }
        )
    return bins


def _score_summary(scores: list[float]) -> dict[str, float | None]:
    if not scores:
        return {"mean": None, "std": None, "min": None, "max": None, "median": None, "n": 0}
    arr = np.asarray(scores, dtype=np.float64)
    return {
        "n": int(arr.size),
        "mean": round(float(np.mean(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "median": round(float(np.median(arr)), 4),
    }


def _load_predictions_scores(predictions_path: Path) -> dict[str, Any]:
    """Load score distributions from ``predictions.csv`` when present."""
    if not predictions_path.is_file():
        return {"available": False, "path": str(predictions_path)}

    rows: list[dict[str, str]] = []
    with predictions_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(dict(row))

    by_split: dict[str, list[float]] = defaultdict(list)
    by_split_label: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    by_lang: dict[str, list[float]] = defaultdict(list)

    for row in rows:
        score_raw = row.get("score_fake", "")
        if not score_raw:
            continue
        score = float(score_raw)
        split = str(row.get("split", "unknown"))
        label = str(row.get("label", "unknown"))
        lang = str(row.get("language", "unknown"))
        by_split[split].append(score)
        by_split_label[split][label].append(score)
        by_lang[lang].append(score)

    split_profiles: dict[str, Any] = {}
    for split, scores in sorted(by_split.items()):
        label_profiles: dict[str, Any] = {}
        for label, label_scores in sorted(by_split_label[split].items()):
            label_profiles[label] = {
                "summary": _score_summary(label_scores),
                "histogram": _score_distribution_bins(label_scores),
            }
        split_profiles[split] = {
            "summary": _score_summary(scores),
            "histogram": _score_distribution_bins(scores),
            "by_label": label_profiles,
        }

    return {
        "available": True,
        "path": str(predictions_path),
        "n_rows": len(rows),
        "by_split": split_profiles,
        "by_language": {
            lang: _score_summary(scores) for lang, scores in sorted(by_lang.items())
        },
    }


def build_final_analysis(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
    train_report_path: Path | None = None,
    predictions_path: Path | None = None,
) -> dict[str, Any]:
    """Build deep split analysis suitable for ``final_analysis.json``.

    Args:
        repo_root: Repository root.
        manifest_path: Publication manifest JSONL.
        train_report_path: Primary training report.
        predictions_path: Optional per-clip predictions CSV.

    Returns:
        Canonical deep-analysis payload for ``split_diagnostics/final_analysis.json``.
    """
    repo_root = repo_root.resolve()
    manifest = manifest_path or (repo_root / "data" / "publication_corpus" / "manifest.jsonl")
    report_path = train_report_path or (
        repo_root / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    )
    preds = predictions_path or (
        repo_root / "artifacts" / "experiments" / "baseline_v1" / "predictions.csv"
    )

    clips: list[ClipMetadata] = _load_rows(manifest) if manifest.is_file() else []
    split_profiles = {
        split.value: _split_profile(clips, split)
        for split in (Split.TRAIN, Split.VAL, Split.TEST)
    }

    train_report: dict[str, Any] = {}
    if report_path.is_file():
        raw = json.loads(report_path.read_text(encoding="utf-8"))
        train_report = raw if isinstance(raw, dict) else {}

    val_metrics = train_report.get("validation_metrics") or {}
    test_metrics = train_report.get("test_metrics") or {}
    val_acc = float(val_metrics.get("accuracy", 0.0) or 0.0)
    test_acc = float(test_metrics.get("accuracy", 0.0) or 0.0)

    val_per_lang = val_metrics.get("per_language") or {}
    test_per_lang = test_metrics.get("per_language") or {}
    lang_gaps: dict[str, dict[str, float | int | None]] = {}
    for lang in ("hi", "mr", "ta"):
        v = val_per_lang.get(lang) or {}
        t = test_per_lang.get(lang) or {}
        if not v and not t:
            continue
        v_acc = float(v.get("accuracy", 0.0)) if v else None
        t_acc = float(t.get("accuracy", 0.0)) if t else None
        lang_gaps[lang] = {
            "val_n": v.get("n"),
            "test_n": t.get("n"),
            "val_speakers": split_profiles["val"]["speakers_per_language"].get(lang),
            "test_speakers": split_profiles["test"]["speakers_per_language"].get(lang),
            "val_accuracy": round(v_acc, 4) if v_acc is not None else None,
            "test_accuracy": round(t_acc, 4) if t_acc is not None else None,
            "accuracy_gap_test_minus_val": (
                round(t_acc - v_acc, 4)
                if v_acc is not None and t_acc is not None
                else None
            ),
        }

    score_distributions = _load_predictions_scores(preds)

    hypotheses: list[str] = []
    if test_acc - val_acc > 0.04:
        hypotheses.append(
            "test_accuracy_exceeds_validation_by>4pp: may reflect small/heterogeneous val "
            "cells (not necessarily leakage)"
        )
    for lang, gap in lang_gaps.items():
        v_acc = gap.get("val_accuracy")
        t_acc = gap.get("test_accuracy")
        if v_acc is None or t_acc is None:
            continue
        if abs(float(v_acc) - float(t_acc)) > 0.20:
            hypotheses.append(
                f"large_val_test_gap_{lang}: val_acc={v_acc} test_acc={t_acc} "
                f"(val_n={gap.get('val_n')} test_n={gap.get('test_n')})"
            )

    test_clips = [c for c in clips if c.split == Split.TEST]
    source_label_map: dict[str, set[str]] = defaultdict(set)
    for clip in test_clips:
        source_label_map[clip.source.value].add(clip.label.value)
    if any(len(labels) == 1 for labels in source_label_map.values()):
        hypotheses.append(
            "source_label_confound: at least one dataset source maps to a single label on test"
        )

    val_lang_counts = split_profiles["val"]["languages"]
    test_lang_counts = split_profiles["test"]["languages"]
    for lang in ("hi", "mr", "ta"):
        val_n = int(val_lang_counts.get(lang, 0))
        test_n = int(test_lang_counts.get(lang, 0))
        if val_n > 0 and test_n > 0 and abs(val_n - test_n) / max(val_n, test_n) > 0.35:
            hypotheses.append(
                f"lang_count_imbalance_{lang}: val_n={val_n} test_n={test_n}"
            )

    return {
        "experiment_id": "split_diagnostics",
        "manifest_path": str(manifest),
        "train_report_path": str(report_path),
        "splits": split_profiles,
        "duration_stats": {
            split: split_profiles[split]["duration_sec"]
            for split in ("train", "val", "test")
        },
        "score_distributions": score_distributions,
        "validation_metrics": {
            "accuracy": val_metrics.get("accuracy"),
            "eer": val_metrics.get("eer"),
            "per_language": val_per_lang,
        },
        "test_metrics": {
            "accuracy": test_metrics.get("accuracy"),
            "eer": test_metrics.get("eer"),
            "per_language": test_per_lang,
        },
        "accuracy_gap_test_minus_val": round(test_acc - val_acc, 4),
        "per_language_gaps": lang_gaps,
        "hypotheses": hypotheses,
        "conclusion": (
            "If Tamil validation was weak while test Tamil was strong, inspect per-language "
            "speaker counts and val cell sizes before assuming leakage. "
            "Cause remains unresolved without per-clip error traces."
        ),
    }


def diagnose_validation_test_gap(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
    train_report_path: Path | None = None,
    predictions_path: Path | None = None,
) -> dict[str, Any]:
    """Compare val/test composition and persisted metrics.

    Args:
        repo_root: Repository root.
        manifest_path: Publication manifest JSONL.
        train_report_path: Primary training report.
        predictions_path: Optional per-clip predictions CSV.

    Returns:
        Diagnostic payload suitable for ``artifacts/experiments/split_diagnostics/metrics.json``.
    """
    analysis = build_final_analysis(
        repo_root,
        manifest_path=manifest_path,
        train_report_path=train_report_path,
        predictions_path=predictions_path,
    )
    return {
        "experiment_id": analysis["experiment_id"],
        "val_profile": analysis["splits"]["val"],
        "test_profile": analysis["splits"]["test"],
        "train_profile": analysis["splits"]["train"],
        "validation_metrics": analysis["validation_metrics"],
        "test_metrics": analysis["test_metrics"],
        "accuracy_gap_test_minus_val": analysis["accuracy_gap_test_minus_val"],
        "hypotheses": analysis["hypotheses"],
        "conclusion": analysis["conclusion"],
    }


def write_split_diagnostics_artifacts(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
    train_report_path: Path | None = None,
    predictions_path: Path | None = None,
) -> dict[str, str]:
    """Write ``metrics.json`` and ``final_analysis.json`` under split_diagnostics."""
    repo_root = repo_root.resolve()
    dest = repo_root / "artifacts" / "experiments" / "split_diagnostics"
    dest.mkdir(parents=True, exist_ok=True)

    metrics = diagnose_validation_test_gap(
        repo_root,
        manifest_path=manifest_path,
        train_report_path=train_report_path,
        predictions_path=predictions_path,
    )
    final_analysis = build_final_analysis(
        repo_root,
        manifest_path=manifest_path,
        train_report_path=train_report_path,
        predictions_path=predictions_path,
    )

    metrics_path = dest / "metrics.json"
    final_path = dest / "final_analysis.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    final_path.write_text(
        json.dumps(final_analysis, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"metrics": str(metrics_path), "final_analysis": str(final_path)}
