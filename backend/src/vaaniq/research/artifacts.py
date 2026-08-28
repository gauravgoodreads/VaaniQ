"""Canonical experiment artifact layout (single source of truth for metrics).

Persisted under ``artifacts/experiments/<experiment_id>/`` with:
``config.json``, ``metrics.json``, ``provenance.json``, optional ``bootstrap.json``,
``predictions.csv``, and ``plots/``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from vaaniq.training.trainer import _git_sha

log = structlog.get_logger(__name__)

EXPERIMENT_IDS = (
    "baseline_v1",
    "xlsr_main",
    "rq1_compression",
    "rq2_english_control",
    "rq3_crosslingual",
    "rq4_calibration",
    "rq5_human",
    "external_generalization",
    "benchmark_v2",
    "source_shortcut",
    "split_diagnostics",
)


def artifact_root(repo_root: Path) -> Path:
    """Return ``artifacts/experiments`` under the repository root."""
    return repo_root / "artifacts" / "experiments"


def experiment_dir(repo_root: Path, experiment_id: str) -> Path:
    """Path for one experiment bundle."""
    if experiment_id not in EXPERIMENT_IDS:
        log.warning("unknown_experiment_id", experiment_id=experiment_id)
    return artifact_root(repo_root) / experiment_id


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def sync_baseline_v1_from_train_report(
    repo_root: Path,
    *,
    train_report_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Copy Baseline V1 metrics from ``train_report.json`` without altering values.

    Args:
        repo_root: Repository root.
        train_report_path: Override path to primary training report.
        manifest_path: Optional publication manifest for provenance hash.

    Returns:
        Summary of written artifact paths.
    """
    report_path = train_report_path or (
        repo_root / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    )
    if not report_path.is_file():
        msg = f"train_report missing: {report_path}"
        raise FileNotFoundError(msg)

    report = _load_json(report_path)
    dest = experiment_dir(repo_root, "baseline_v1")
    dest.mkdir(parents=True, exist_ok=True)

    sha, dirty = _git_sha()
    manifest = manifest_path or (repo_root / "data" / "publication_corpus" / "manifest.jsonl")
    manifest_hash = _sha256_file(manifest)

    config: dict[str, Any] = {
        "experiment_id": "baseline_v1",
        "benchmark_level": 1,
        "title": "VaaniQ Bounded Publication Benchmark / Baseline V1",
        "description": (
            "Speaker-disjoint Kathbath-real + IndicSynth-fake subset; "
            "deterministic acoustic-embedding front-end + AASIST-compatible head."
        ),
        "front_end": report.get("front_end", "acoustic_embedding_1024d"),
        "pipeline": report.get("pipeline"),
        "seed": report.get("seed", 42),
        "git_sha": sha,
        "git_dirty": dirty,
        "train_report_source": str(report_path.relative_to(repo_root))
        if report_path.is_relative_to(repo_root)
        else str(report_path),
        "checkpoint_npz": "models/checkpoints/xlsr_aasist/aasist-v1.npz",
        "created_at": datetime.now(UTC).isoformat(),
    }
    _write_json(dest / "config.json", config)

    metrics: dict[str, Any] = {
        "experiment_id": "baseline_v1",
        "n_train": report.get("n_train"),
        "n_val": report.get("n_val"),
        "n_test": report.get("n_test"),
        "n_clips": report.get("n_clips"),
        "total_hours": report.get("total_hours"),
        "data_provenance": report.get("data_provenance"),
        "speaker_disjoint_verified": report.get("speaker_disjoint_verified"),
        "validation_metrics": report.get("validation_metrics"),
        "test_metrics": report.get("test_metrics"),
        "eval_metrics": report.get("eval_metrics"),
        "calibration_pre": report.get("calibration_pre")
        or (report.get("test_metrics") or {}).get("calibration_pre"),
        "calibration_post": report.get("calibration_post")
        or (report.get("test_metrics") or {}).get("calibration_post"),
        "min_dcf_config": {
            "p_target": 0.05,
            "c_miss": 1.0,
            "c_fa": 1.0,
            "note": "ASVspoof-style defaults (OQ-018)",
        },
        "synced_at": datetime.now(UTC).isoformat(),
        "source_artifact": str(report_path),
    }
    _write_json(dest / "metrics.json", metrics)

    provenance_path = repo_root / "data" / "publication_corpus" / "provenance.json"
    provenance: dict[str, Any] = {
        "experiment_id": "baseline_v1",
        "manifest_sha256": manifest_hash,
        "provenance_json": _load_json(provenance_path) if provenance_path.is_file() else {},
        "train_report_sha256": _sha256_file(report_path),
        "checkpoint_sha256": _sha256_file(
            repo_root / "models" / "checkpoints" / "xlsr_aasist" / "aasist-v1.npz"
        ),
        "scope_limitation": (
            "Results apply only to this bounded Kathbath + IndicSynth subset; "
            "real and fake sources are perfectly associated with class labels in V1."
        ),
    }
    _write_json(dest / "provenance.json", provenance)

    # Preserve full train_report as read-only reference
    ref = dest / "train_report.json"
    if report_path.resolve() != ref.resolve():
        shutil.copy2(report_path, ref)

    log.info("baseline_v1_artifacts_synced", dest=str(dest))
    return {
        "experiment_id": "baseline_v1",
        "dest": str(dest),
        "config": str(dest / "config.json"),
        "metrics": str(dest / "metrics.json"),
        "provenance": str(dest / "provenance.json"),
    }


def sync_rq3_from_checkpoints(repo_root: Path) -> dict[str, Any]:
    """Sync leave-one-language-out reports into ``rq3_crosslingual`` artifacts."""
    dest = experiment_dir(repo_root, "rq3_crosslingual")
    dest.mkdir(parents=True, exist_ok=True)
    folds: dict[str, Any] = {}
    for lang in ("hi", "mr", "ta"):
        path = repo_root / "models" / "checkpoints" / "rq3" / f"test_{lang}" / "train_report.json"
        if path.is_file():
            folds[f"held_out_{lang}"] = _load_json(path)
    payload = {
        "experiment_id": "rq3_crosslingual",
        "folds": folds,
        "synced_at": datetime.now(UTC).isoformat(),
    }
    _write_json(dest / "metrics.json", payload)
    _write_json(
        dest / "config.json",
        {
            "experiment_id": "rq3_crosslingual",
            "protocol": "leave_one_language_out",
            "train_languages_per_fold": {
                "held_out_hi": ["mr", "ta"],
                "held_out_mr": ["hi", "ta"],
                "held_out_ta": ["hi", "mr"],
            },
        },
    )
    return {"experiment_id": "rq3_crosslingual", "dest": str(dest), "n_folds": len(folds)}


def write_predictions_csv(
    repo_root: Path,
    experiment_id: str,
    rows: list[dict[str, Any]],
) -> Path:
    """Persist per-instance predictions for calibration / error analysis."""
    dest = experiment_dir(repo_root, experiment_id)
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "predictions.csv"
    if not rows:
        return out
    fieldnames = list(rows[0].keys())
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out


def load_experiment_metrics(repo_root: Path, experiment_id: str) -> dict[str, Any]:
    """Load ``metrics.json`` for document generators."""
    return _load_json(experiment_dir(repo_root, experiment_id) / "metrics.json")
