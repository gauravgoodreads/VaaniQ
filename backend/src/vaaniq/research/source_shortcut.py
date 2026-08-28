"""Source-domain shortcut analysis (P2 / scientific weakness quantification).

Trains simple probes on acoustic embeddings to estimate how easily dataset
source (Kathbath vs IndicSynth) is recovered vs bonafide/deepfake label.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.core.domain.entities import Waveform
from vaaniq.features.acoustic import acoustic_embedding


def _softmax_rows(logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits, axis=1, keepdims=True)
    ex = np.exp(z)
    denom = np.sum(ex, axis=1, keepdims=True)
    return np.asarray(ex / denom, dtype=np.float64)


def _logistic_train(
    X: np.ndarray,
    y: np.ndarray,
    *,
    seed: int,
    epochs: int = 80,
    lr: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Minimal binary logistic regression (NumPy)."""
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.01, size=(X.shape[1],)).astype(np.float64)
    b = np.float64(0.0)
    for _ in range(epochs):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))
        grad_w = (X.T @ (p - y)) / max(1, y.size)
        grad_b = float(np.mean(p - y))
        w -= lr * grad_w
        b -= lr * grad_b
    return w, np.asarray([b], dtype=np.float64)


def _accuracy(scores: np.ndarray, y: np.ndarray, *, threshold: float = 0.5) -> float:
    pred = (scores >= threshold).astype(int)
    return float(np.mean(pred == y))


def _load_features(manifest_path: Path, corpus_root: Path) -> dict[str, Any]:
    pre = DefaultPreprocessor()
    rows: list[dict[str, object]] = []
    with manifest_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    feats: list[np.ndarray] = []
    labels: list[int] = []
    sources: list[str] = []
    splits: list[str] = []
    for row in rows:
        uri = str(row.get("uri", ""))
        path = corpus_root / uri
        if not path.is_file():
            continue
        data, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if getattr(data, "ndim", 1) > 1:
            data = np.mean(data, axis=1)
        wav = pre.transform(
            Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr))
        )
        feats.append(acoustic_embedding(wav, dim=1024))
        labels.append(1 if str(row.get("label")) == "fake" else 0)
        sources.append(str(row.get("source", "unknown")))
        splits.append(str(row.get("split", "train")))

    return {
        "X": np.stack(feats).astype(np.float32),
        "y_label": np.asarray(labels, dtype=np.int64),
        "sources": np.asarray(sources),
        "splits": np.asarray(splits),
    }


def run_source_shortcut_analysis(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Quantify source vs label predictability on held-out test split.

    Args:
        repo_root: Repository root.
        manifest_path: Manifest JSONL path.
        seed: Random seed for logistic probe.

    Returns:
        Metrics comparing label classifier vs source classifier.
    """
    repo_root = repo_root.resolve()
    manifest = manifest_path or (repo_root / "data" / "publication_corpus" / "manifest.jsonl")
    corpus_root = manifest.parent
    if not manifest.is_file():
        msg = f"manifest missing: {manifest}"
        raise FileNotFoundError(msg)

    pack = _load_features(manifest, corpus_root)
    X = pack["X"]
    y_label = pack["y_label"]
    sources = pack["sources"]
    splits = pack["splits"]

    unique_sources = sorted(set(sources.tolist()))
    if len(unique_sources) < 2:
        return {
            "experiment_id": "source_shortcut",
            "error": "need_at_least_two_sources",
            "sources": unique_sources,
        }

    # Binary source probe: first source vs rest (typically kathbath vs indicsynth)
    primary_source = unique_sources[0]
    y_source = (sources != primary_source).astype(np.int64)

    train_mask = splits == "train"
    test_mask = splits == "test"
    if not np.any(test_mask):
        test_mask = ~train_mask

    X_tr = X[train_mask].astype(np.float64)
    X_te = X[test_mask].astype(np.float64)
    y_label_tr, y_label_te = y_label[train_mask], y_label[test_mask]
    y_source_tr, y_source_te = y_source[train_mask], y_source[test_mask]

    # Label probe
    w_l, b_l = _logistic_train(X_tr, y_label_tr.astype(np.float64), seed=seed)
    label_scores = 1.0 / (1.0 + np.exp(-np.clip(X_te @ w_l + b_l[0], -20, 20)))
    label_acc = _accuracy(label_scores, y_label_te)

    # Source probe
    w_s, b_s = _logistic_train(X_tr, y_source_tr.astype(np.float64), seed=seed + 1)
    source_scores = 1.0 / (1.0 + np.exp(-np.clip(X_te @ w_s + b_s[0], -20, 20)))
    source_acc = _accuracy(source_scores, y_source_te)

    # Duration / RMS stats by source (coarse fingerprinting)
    duration_by_source: dict[str, list[float]] = {s: [] for s in unique_sources}
    with manifest.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            src = str(row.get("source", "unknown"))
            dur = row.get("duration_sec")
            if isinstance(dur, int | float):
                duration_by_source.setdefault(src, []).append(float(dur))

    duration_summary = {
        src: {
            "mean_sec": round(float(np.mean(vals)), 4) if vals else None,
            "std_sec": round(float(np.std(vals)), 4) if vals else None,
            "n": len(vals),
        }
        for src, vals in duration_by_source.items()
    }

    interpretation = (
        "If source classification accuracy on test exceeds label classification, "
        "the benchmark may be partially solvable via dataset fingerprints (Baseline V1 confound). "
        "Benchmark V2 with multi-source real/fake is intended to reduce this dependence."
    )
    if source_acc > label_acc + 0.05:
        interpretation += (
            f" Observed: source probe test accuracy ({source_acc:.3f}) "
            f"> label probe ({label_acc:.3f}) by >5pp."
        )

    return {
        "experiment_id": "source_shortcut",
        "sources": unique_sources,
        "primary_source_baseline": primary_source,
        "test_n": int(np.sum(test_mask)),
        "label_probe_test_accuracy": round(label_acc, 4),
        "source_probe_test_accuracy": round(source_acc, 4),
        "source_beats_label_by_pp": round((source_acc - label_acc) * 100, 2),
        "duration_by_source": duration_summary,
        "interpretation": interpretation,
        "benchmark_v1_confound": True,
    }
