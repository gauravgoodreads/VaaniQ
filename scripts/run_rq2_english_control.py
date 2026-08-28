#!/usr/bin/env python3
"""RQ2: English-only ASVspoof-style control vs multilingual Indic evaluation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))


def _load_dotenv() -> None:
    env_path = _REPO / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _stream_asvspoof_la(*, max_clips: int, seed: int) -> list[tuple[np.ndarray, int, int]]:
    """Stream ASVspoof 2019 LA train via byte decode (avoids torchcodec on Windows)."""
    import io

    from datasets import Audio, load_dataset

    ds = load_dataset("Bisher/ASVspoof_2019_LA", split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))
    ds = ds.shuffle(seed=seed, buffer_size=500)
    out: list[tuple[np.ndarray, int, int]] = []
    for row in ds:
        if len(out) >= max_clips:
            break
        try:
            audio = row.get("audio")
            if not isinstance(audio, dict):
                continue
            payload = audio.get("bytes")
            if not isinstance(payload, bytes) or not payload:
                path = audio.get("path")
                if isinstance(path, str) and Path(path).is_file():
                    samples, sr = sf.read(path, dtype="float32", always_2d=False)
                else:
                    continue
            else:
                samples, sr = sf.read(io.BytesIO(payload), dtype="float32", always_2d=False)
            if getattr(samples, "ndim", 1) > 1:
                samples = np.mean(samples, axis=1)
            label_raw = row.get("label", row.get("key", "bonafide"))
            if isinstance(label_raw, int):
                label = 0 if label_raw == 0 else 1
            else:
                label = 0 if str(label_raw).lower() in {"bonafide", "real", "0"} else 1
            out.append((samples.astype(np.float32), label, int(sr)))
        except Exception:
            continue
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-clips", type=int, default=400)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--indic-corpus",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
    )
    args = parser.parse_args()
    _load_dotenv()

    from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
    from vaaniq.core.domain.entities import Waveform
    from vaaniq.evaluation.metrics.core import (
        bootstrap_metric_ci,
        classification_report_scores,
        confusion_matrix,
        equal_error_rate,
        min_dcf,
        roc_curve,
    )
    from vaaniq.evaluation.score_contract import (
        logits_to_fake_scores,
        mean_scores_by_label,
        score_polarity_audit,
    )
    from vaaniq.features.acoustic import acoustic_embedding
    from vaaniq.models.aasist.classifier import AASISTClassifier

    print("streaming English ASVspoof LA clips...")
    try:
        english = _stream_asvspoof_la(max_clips=args.english_clips, seed=args.seed)
    except Exception as exc:
        dest = _REPO / "artifacts" / "experiments" / "rq2_english_control"
        dest.mkdir(parents=True, exist_ok=True)
        err = {"status": "BLOCKED", "reason": str(exc), "dataset": "Bisher/ASVspoof_2019_LA train"}
        (dest / "metrics.json").write_text(json.dumps(err, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(err, indent=2))
        return 1

    if len(english) < 50:
        msg = f"insufficient English clips: {len(english)}"
        raise SystemExit(msg)

    pre = DefaultPreprocessor()
    X_en: list[np.ndarray] = []
    y_en: list[int] = []
    for samples, label, sr in english:
        wav = pre.transform(Waveform(samples=samples, sample_rate_hz=sr))
        X_en.append(acoustic_embedding(wav, dim=1024))
        y_en.append(label)
    X_en_arr = np.stack(X_en).astype(np.float32)
    y_en_arr = np.asarray(y_en, dtype=np.int64)

    cut = int(X_en_arr.shape[0] * 0.85)
    X_tr, y_tr = X_en_arr[:cut], y_en_arr[:cut]
    X_val, y_val = X_en_arr[cut:], y_en_arr[cut:]

    clf_en = AASISTClassifier(rng=np.random.default_rng(args.seed))
    best_w = {k: v.copy() for k, v in clf_en._weights.items()}
    best_acc = -1.0
    for epoch in range(80):
        loss = clf_en.train_numpy_epoch(X_tr, y_tr, learning_rate=0.04, batch_size=32)
        acc = float(np.mean(np.argmax(clf_en.predict_batch(X_val), axis=1) == y_val))
        if acc > best_acc:
            best_acc = acc
            best_w = {k: v.copy() for k, v in clf_en._weights.items()}
        if epoch % 20 == 0:
            print(f"english epoch={epoch} loss={loss:.4f} val_acc={acc:.4f}")
    clf_en._weights = best_w

    # Evaluate on Indic held-out test (same protocol as multilingual)
    rows: list[dict[str, object]] = []
    with (args.indic_corpus / "manifest.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    X_te: list[np.ndarray] = []
    y_te: list[int] = []
    for row in rows:
        if str(row.get("split")) != "test":
            continue
        path = args.indic_corpus / str(row.get("uri", ""))
        if not path.is_file():
            continue
        data, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if getattr(data, "ndim", 1) > 1:
            data = np.mean(data, axis=1)
        wav = pre.transform(Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr)))
        X_te.append(acoustic_embedding(wav, dim=1024))
        y_te.append(1 if str(row.get("label")) == "fake" else 0)
    X_te_arr = np.stack(X_te).astype(np.float32)
    y_te_arr = np.asarray(y_te, dtype=np.int64)

    logits = clf_en.predict_batch(X_te_arr)
    scores_arr = logits_to_fake_scores(logits)
    scores = scores_arr.tolist()
    labels = y_te_arr.astype(int).tolist()
    rep = classification_report_scores(scores, labels)
    eer = equal_error_rate(scores, labels)
    eer_pt, eer_lo, eer_hi = bootstrap_metric_ci(scores, labels, metric="eer", seed=args.seed)
    _, _, auc = roc_curve(scores, labels)
    polarity = score_polarity_audit(scores, labels)
    score_means = mean_scores_by_label(scores, labels)
    cm = confusion_matrix(scores, labels)

    manifest_path = _REPO / "artifacts" / "final_results_manifest.json"
    if manifest_path.is_file():
        multi_test = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            .get("baseline_v1", {})
            .get("metrics", {})
        )
    else:
        multilingual = json.loads(
            (_REPO / "artifacts/experiments/baseline_v1/metrics.json").read_text(encoding="utf-8")
        )
        multi_test = multilingual.get("test_metrics") or {}

    result = {
        "experiment_id": "rq2_english_control",
        "english_train_n": int(X_tr.shape[0]),
        "english_val_n": int(X_val.shape[0]),
        "indic_test_n": int(X_te_arr.shape[0]),
        "score_contract": {
            "label_fake": 1,
            "threshold": 0.5,
            "higher_score_means": "more_fake",
        },
        "english_only_indic_test": {
            **rep,
            "eer": round(eer, 4),
            "eer_95ci": [round(eer_pt, 4), round(eer_lo, 4), round(eer_hi, 4)],
            "min_dcf": round(min_dcf(scores, labels), 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
            "score_means_by_label": score_means,
            "polarity_audit": polarity,
        },
        "multilingual_baseline_v1_test": {
            "accuracy": multi_test.get("accuracy"),
            "eer": multi_test.get("eer"),
            "f1": multi_test.get("f1"),
            "roc_auc": multi_test.get("roc_auc"),
        },
        "polarity_interpretation": (
            "If likely_score_inversion is True, scores may be reversed relative to "
            "the canonical contract; do not flip without verifying ASVspoof label mapping. "
            "If False and ROC-AUC << 0.5, catastrophic English-to-Indic domain shift is likely."
        ),
        "conclusion": (
            "English-only ASVspoof LA-trained control evaluated on Indic test protocol."
        ),
        "dataset": "Bisher/ASVspoof_2019_LA train (streaming subset, ODC-By)",
    }
    dest = _REPO / "artifacts/experiments" / "rq2_english_control"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
