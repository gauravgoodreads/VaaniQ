#!/usr/bin/env python3
"""Train the VaaniQ AASIST head on the local demo corpus (hi/mr/ta accents)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.calibration.ece import brier_score, expected_calibration_error
from vaaniq.core.domain.entities import Waveform
from vaaniq.evaluation.metrics.core import (
    bootstrap_metric_ci,
    classification_report_scores,
    confusion_matrix,
    equal_error_rate,
    min_dcf,
    roc_curve,
)
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.models.aasist.classifier import AASISTClassifier


def _load_manifest(root: Path) -> list[dict[str, object]]:
    path = root / "manifest.jsonl"
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _softmax_rows(logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits, axis=1, keepdims=True)
    ex = np.exp(z)
    return ex / np.sum(ex, axis=1, keepdims=True)


def _accuracy(clf: AASISTClassifier, X: np.ndarray, y: np.ndarray) -> float:
    logits = clf.predict_batch(X)
    pred = np.argmax(logits, axis=1)
    return float(np.mean(pred == y))


def _fake_scores(clf: AASISTClassifier, X: np.ndarray) -> np.ndarray:
    logits = clf.predict_batch(X)
    probs = _softmax_rows(logits)
    return probs[:, 1].astype(np.float64)


def _eval_pack(
    clf: AASISTClassifier,
    X: np.ndarray,
    y: np.ndarray,
    *,
    langs: np.ndarray | None = None,
    conditions: np.ndarray | None = None,
) -> dict[str, object]:
    scores = _fake_scores(clf, X)
    labels = y.astype(int).tolist()
    score_list = scores.tolist()
    probs = _softmax_rows(clf.predict_batch(X))
    conf = np.max(probs, axis=1).tolist()
    pred = (scores >= 0.5).astype(int)
    correct = (pred == y).astype(int).tolist()
    _, _, roc_auc = roc_curve(score_list, labels)
    eer_point, eer_lo, eer_hi = bootstrap_metric_ci(
        score_list, labels, metric="eer", n_samples=1000, seed=42
    )
    dcf_point, dcf_lo, dcf_hi = bootstrap_metric_ci(
        score_list, labels, metric="min_dcf", n_samples=1000, seed=42
    )
    pack: dict[str, object] = {
        "n": int(y.size),
        "accuracy": round(_accuracy(clf, X, y), 4),
        "eer": round(equal_error_rate(score_list, labels), 4),
        "min_dcf": round(min_dcf(score_list, labels), 4),
        "roc_auc": round(roc_auc, 4),
        "ece": round(expected_calibration_error(conf, correct), 4),
        "brier": round(brier_score(score_list, labels), 4),
        "confusion_matrix": confusion_matrix(score_list, labels),
        "eer_95ci": [round(eer_point, 4), round(eer_lo, 4), round(eer_hi, 4)],
        "min_dcf_95ci": [round(dcf_point, 4), round(dcf_lo, 4), round(dcf_hi, 4)],
        **{k: round(v, 4) for k, v in classification_report_scores(score_list, labels).items()},
    }
    if langs is not None:
        per_lang: dict[str, dict[str, float | int]] = {}
        for lang in ("hi", "mr", "ta"):
            mask = langs == lang
            if not np.any(mask):
                continue
            s = scores[mask].tolist()
            lab = y[mask].astype(int).tolist()
            per_lang[lang] = {
                "n": int(np.sum(mask)),
                "accuracy": round(float(np.mean((scores[mask] >= 0.5) == y[mask])), 4),
                "eer": round(equal_error_rate(s, lab), 4),
                "min_dcf": round(min_dcf(s, lab), 4),
                "f1": round(classification_report_scores(s, lab)["f1"], 4),
            }
        pack["per_language"] = per_lang
    if conditions is not None:
        per_condition: dict[str, dict[str, float | int]] = {}
        for condition in ("clean", "opus_whatsapp_sim"):
            mask = conditions == condition
            if not np.any(mask):
                continue
            s = scores[mask].tolist()
            lab = y[mask].astype(int).tolist()
            per_condition[condition] = {
                "n": int(np.sum(mask)),
                "accuracy": round(float(np.mean((scores[mask] >= 0.5) == y[mask])), 4),
                "eer": round(equal_error_rate(s, lab), 4),
                "min_dcf": round(min_dcf(s, lab), 4),
                "f1": round(classification_report_scores(s, lab)["f1"], 4),
            }
        pack["per_condition"] = per_condition
    return pack


def _seed_linear_separation(clf: AASISTClassifier, X: np.ndarray, y: np.ndarray) -> None:
    h = np.tanh(X @ clf._weights["proj_w"] + clf._weights["proj_b"]).astype(np.float32)
    mu0 = h[y == 0].mean(axis=0) if np.any(y == 0) else np.zeros(h.shape[1], dtype=np.float32)
    mu1 = h[y == 1].mean(axis=0) if np.any(y == 1) else np.zeros(h.shape[1], dtype=np.float32)
    direction = (mu1 - mu0).astype(np.float32)
    norm = float(np.linalg.norm(direction)) + 1e-8
    direction = direction / norm
    clf._weights["out_w"][:, 0] = (-2.2 * direction).astype(np.float32)
    clf._weights["out_w"][:, 1] = (2.2 * direction).astype(np.float32)
    clf._weights["out_b"][0] = np.float32(0.35)
    clf._weights["out_b"][1] = np.float32(-0.35)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "demo_corpus",
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lr", type=float, default=0.04)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--noise-std", type=float, default=0.06)
    args = parser.parse_args()

    rows = _load_manifest(args.corpus)
    if not rows:
        raise SystemExit("No manifest — run generate_demo_corpus.py first")

    pre = DefaultPreprocessor()
    feats: list[np.ndarray] = []
    labels: list[int] = []
    langs: list[str] = []
    conditions: list[str] = []
    splits: list[str] = []
    for row in rows:
        uri = str(row.get("uri", ""))
        path = args.corpus / uri
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
        langs.append(str(row.get("language", "hi")))
        conditions.append(str(row.get("compression_status", "clean")))
        splits.append(str(row.get("split", "train")))

    X = np.stack(feats).astype(np.float32)
    y = np.asarray(labels, dtype=np.int64)
    lang_arr = np.asarray(langs)
    condition_arr = np.asarray(conditions)
    split_arr = np.asarray(splits)

    # Respect the versioned manifest. Test rows never enter training or checkpoint selection.
    train_mask = split_arr == "train"
    val_mask = split_arr == "val"
    test_mask = split_arr == "test"
    X_val, y_val = X[val_mask], y[val_mask]
    lang_val = lang_arr[val_mask]
    condition_val = condition_arr[val_mask]
    X_tr, y_tr = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    lang_test = lang_arr[test_mask]
    condition_test = condition_arr[test_mask]

    clf = AASISTClassifier(rng=np.random.default_rng(args.seed))
    _seed_linear_separation(clf, X_tr, y_tr)
    print(f"seeded_val_acc={_accuracy(clf, X_val, y_val):.4f}")

    best_acc = -1.0
    best_eer = 1.0
    best_weights = {k: v.copy() for k, v in clf._weights.items()}
    rng = np.random.default_rng(args.seed)

    for epoch in range(args.epochs):
        X_aug = X_tr + rng.normal(0.0, args.noise_std, size=X_tr.shape).astype(np.float32)
        loss = clf.train_numpy_epoch(X_aug, y_tr, learning_rate=args.lr, batch_size=args.batch_size)
        acc = _accuracy(clf, X_val, y_val)
        scores = _fake_scores(clf, X_val)
        eer = equal_error_rate(scores.tolist(), y_val.tolist())
        # Standard checkpoint selection: highest validation accuracy, then lowest EER.
        if acc > best_acc or (acc == best_acc and eer < best_eer):
            best_acc = acc
            best_eer = eer
            best_weights = {k: v.copy() for k, v in clf._weights.items()}
        if epoch % 10 == 0 or epoch == args.epochs - 1:
            print(f"epoch={epoch} loss={loss:.4f} val_acc={acc:.4f} eer={eer:.4f}")

    clf._weights = best_weights
    val_metrics = _eval_pack(clf, X_val, y_val, langs=lang_val, conditions=condition_val)
    test_metrics = _eval_pack(clf, X_test, y_test, langs=lang_test, conditions=condition_test)

    repo = Path(__file__).resolve().parents[1]
    out = repo / "models" / "checkpoints" / "xlsr_aasist" / "aasist-v1.npz"
    clf.save(out)

    from vaaniq.calibration.temperature import TemperatureScaler
    from vaaniq.core.domain.entities import Logits
    from vaaniq.core.types import CompressionCondition, Label, Language

    val_logits = clf.predict_batch(X_val)
    scaler = TemperatureScaler()
    logit_objs = [
        Logits(values=row.astype(np.float32), class_order=(Label.REAL, Label.FAKE))
        for row in val_logits
    ]
    for lang in (Language.HI, Language.MR, Language.TA):
        for cond in (CompressionCondition.CLEAN, CompressionCondition.OPUS_WHATSAPP_SIM):
            cell_mask = (lang_val == lang.value) & (condition_val == cond.value)
            cell_logits = [item for item, keep in zip(logit_objs, cell_mask, strict=True) if keep]
            cell_labels = y_val[cell_mask].astype(int).tolist()
            if not cell_logits:
                continue
            scaler.fit(
                cell_logits,
                cell_labels,
                language=lang,
                condition=cond,
            )

    def apply_calibration(
        logits: np.ndarray,
        labels: np.ndarray,
        languages: np.ndarray,
        compression_conditions: np.ndarray,
    ) -> dict[str, float]:
        calibrated: list[np.ndarray] = []
        for row, lang_raw, condition_raw in zip(
            logits,
            languages,
            compression_conditions,
            strict=True,
        ):
            probability = scaler.transform(
                Logits(
                    values=row.astype(np.float32),
                    class_order=(Label.REAL, Label.FAKE),
                ),
                language=Language(str(lang_raw)),
                condition=CompressionCondition(str(condition_raw)),
            )
            calibrated.append(probability.values)
        probabilities = np.stack(calibrated)
        predictions = np.argmax(probabilities, axis=1)
        confidences = np.max(probabilities, axis=1)
        correct = (predictions == labels).astype(int)
        return {
            "ece": round(
                expected_calibration_error(confidences.tolist(), correct.tolist()),
                4,
            ),
            "brier": round(
                brier_score(probabilities[:, 1].tolist(), labels.astype(int).tolist()),
                4,
            ),
        }

    val_post_calibration = apply_calibration(
        val_logits,
        y_val,
        lang_val,
        condition_val,
    )
    test_post_calibration = apply_calibration(
        clf.predict_batch(X_test),
        y_test,
        lang_test,
        condition_test,
    )
    val_metrics["calibration_pre"] = {
        "ece": val_metrics["ece"],
        "brier": val_metrics["brier"],
    }
    val_metrics["calibration_post"] = val_post_calibration
    test_metrics["calibration_pre"] = {
        "ece": test_metrics["ece"],
        "brier": test_metrics["brier"],
    }
    test_metrics["calibration_post"] = test_post_calibration
    val_metrics["ece"] = val_post_calibration["ece"]
    val_metrics["brier"] = val_post_calibration["brier"]
    test_metrics["ece"] = test_post_calibration["ece"]
    test_metrics["brier"] = test_post_calibration["brier"]
    temp_path = out.with_name("temperatures.json")
    scaler.save(temp_path)

    total_hours = sum(float(r.get("duration_sec", 12.0)) for r in rows) / 3600.0
    meta = {
        "n_train": len(y_tr),
        "n_val": len(y_val),
        "n_test": len(y_test),
        "n_clips": len(y),
        "total_hours": round(total_hours, 2),
        "val_accuracy": float(val_metrics["accuracy"]),
        "val_eer": float(val_metrics["eer"]),
        "val_min_dcf": float(val_metrics["min_dcf"]),
        "val_ece": float(val_metrics["ece"]),
        "val_brier": float(val_metrics["brier"]),
        "test_accuracy": float(test_metrics["accuracy"]),
        "test_eer": float(test_metrics["eer"]),
        "test_min_dcf": float(test_metrics["min_dcf"]),
        "test_roc_auc": float(test_metrics["roc_auc"]),
        "test_ece": float(test_metrics["ece"]),
        "test_brier": float(test_metrics["brier"]),
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "eval_metrics": test_metrics,
        "checkpoint": str(out),
        "temperatures": str(temp_path),
        "temperature_table": scaler.as_dict(),
        "languages": ["hi", "mr", "ta"],
        "cuda_available": False,
        "data_provenance": "synthetic_demo_only",
        "split_protocol": "manifest train/val/test; test excluded from training and selection",
        "note": (
            "Measured on an expanded synthetic hi/mr/ta demo corpus with "
            "legitimate difficult examples; not a publication result."
        ),
        "pipeline": "preprocess -> acoustic embedding -> AASIST head -> temperature scaling",
        "status": "trained_calibrated",
    }
    try:
        import torch

        meta["cuda_available"] = bool(torch.cuda.is_available())
        if meta["cuda_available"]:
            meta["gpu"] = torch.cuda.get_device_name(0)
    except Exception:
        pass
    out.with_name("train_report.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
