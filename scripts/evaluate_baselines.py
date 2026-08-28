#!/usr/bin/env python3
"""Evaluate LFCC-GMM and RawNet2 baselines on the publication benchmark protocol."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.types import Label
from vaaniq.evaluation.metrics.core import (
    bootstrap_metric_ci,
    classification_report_scores,
    equal_error_rate,
    min_dcf,
    roc_curve,
)
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.baselines.lfcc_gmm.classifier import LfccGmmClassifier
from vaaniq.models.baselines.rawnet2.classifier import RawNet2Classifier


def _load_rows(corpus: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with (corpus / "manifest.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _load_waveforms(corpus: Path, rows: list[dict[str, object]]) -> tuple[list[Waveform], list[dict[str, object]]]:
    pre = DefaultPreprocessor()
    waveforms: list[Waveform] = []
    kept: list[dict[str, object]] = []
    for row in rows:
        path = corpus / str(row.get("uri", ""))
        if not path.is_file():
            continue
        data, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if getattr(data, "ndim", 1) > 1:
            data = np.mean(data, axis=1)
        waveforms.append(
            pre.transform(
                Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr))
            )
        )
        kept.append(row)
    return waveforms, kept


def _scores_from_logits(logits: np.ndarray) -> list[float]:
    z = logits - np.max(logits, axis=1, keepdims=True)
    ex = np.exp(z)
    probs = ex / np.sum(ex, axis=1, keepdims=True)
    return probs[:, 1].astype(np.float64).tolist()


def _eval_model(
    scores: list[float],
    labels: list[int],
    *,
    model_name: str,
) -> dict[str, object]:
    eer = equal_error_rate(scores, labels)
    _, _, auc = roc_curve(scores, labels)
    eer_pt, eer_lo, eer_hi = bootstrap_metric_ci(scores, labels, metric="eer", seed=42)
    rep = classification_report_scores(scores, labels)
    return {
        "model": model_name,
        "n": len(labels),
        "accuracy": round(rep["accuracy"], 4),
        "precision": round(rep["precision"], 4),
        "recall": round(rep["recall"], 4),
        "f1": round(rep["f1"], 4),
        "eer": round(eer, 4),
        "eer_95ci": [round(eer_pt, 4), round(eer_lo, 4), round(eer_hi, 4)],
        "min_dcf": round(min_dcf(scores, labels), 4),
        "roc_auc": round(auc, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--aasist-checkpoint", type=Path, default=None)
    args = parser.parse_args()

    rows = _load_rows(args.corpus)
    waveforms, kept = _load_waveforms(args.corpus, rows)
    splits = [str(r.get("split", "train")) for r in kept]
    labels = [Label.FAKE if str(r.get("label")) == "fake" else Label.REAL for r in kept]
    y_int = [1 if lab == Label.FAKE else 0 for lab in labels]

    train_idx = [i for i, s in enumerate(splits) if s == "train"]
    test_idx = [i for i, s in enumerate(splits) if s == "test"]
    train_wavs = [waveforms[i] for i in train_idx]
    train_labels = [labels[i] for i in train_idx]
    test_wavs = [waveforms[i] for i in test_idx]
    test_y = [y_int[i] for i in test_idx]

    results: dict[str, object] = {"experiment_id": "baseline_matrix", "models": {}}

    # LFCC-GMM
    lfcc = LfccGmmClassifier(rng=np.random.default_rng(args.seed))
    lfcc.fit(train_wavs, train_labels)
    lfcc_scores: list[float] = []
    for wav in test_wavs:
        logits = lfcc.predict_waveform(wav)
        lfcc_scores.append(float(logits.values[1]))
    results["models"]["lfcc_gmm"] = _eval_model(lfcc_scores, test_y, model_name="lfcc_gmm")

    # RawNet2-style approximate baseline
    rawnet = RawNet2Classifier(rng=np.random.default_rng(args.seed))
    for _ in range(12):
        rawnet.train_epoch(train_wavs, train_labels, learning_rate=0.08)
    rn_scores: list[float] = []
    for wav in test_wavs:
        logits = rawnet.predict_waveform(wav)
        rn_scores.append(float(logits.values[1]))
    results["models"]["rawnet2_style_approx"] = _eval_model(
        rn_scores, test_y, model_name="rawnet2_style_approx"
    )

    # Acoustic + AASIST (Baseline V1 checkpoint)
    ckpt = args.aasist_checkpoint or (
        _REPO / "models" / "checkpoints" / "xlsr_aasist" / "aasist-v1.npz"
    )
    aasist = AASISTClassifier(rng=np.random.default_rng(args.seed))
    if ckpt.is_file():
        aasist.load(ckpt)
        X_test = np.stack([acoustic_embedding(w, dim=1024) for w in test_wavs]).astype(np.float32)
        aasist_scores = _scores_from_logits(aasist.predict_batch(X_test))
        results["models"]["acoustic_aasist_v1"] = _eval_model(
            aasist_scores, test_y, model_name="acoustic_aasist_v1"
        )
    else:
        results["models"]["acoustic_aasist_v1"] = {"skipped": f"missing checkpoint {ckpt}"}

    dest = _REPO / "artifacts" / "experiments" / "baseline_matrix"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
