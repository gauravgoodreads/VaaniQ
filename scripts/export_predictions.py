#!/usr/bin/env python3
"""Export test-set predictions and run calibration audit from a trained checkpoint."""

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
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.research.artifacts import write_predictions_csv
from vaaniq.research.calibration_audit import run_calibration_audit


def _load_manifest(corpus: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with (corpus / "manifest.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _embed_corpus(corpus: Path, rows: list[dict[str, object]]) -> tuple[np.ndarray, list[dict[str, object]]]:
    pre = DefaultPreprocessor()
    feats: list[np.ndarray] = []
    kept: list[dict[str, object]] = []
    for row in rows:
        path = corpus / str(row.get("uri", ""))
        if not path.is_file():
            continue
        data, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if getattr(data, "ndim", 1) > 1:
            data = np.mean(data, axis=1)
        wav = pre.transform(
            Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr))
        )
        feats.append(acoustic_embedding(wav, dim=1024))
        kept.append(row)
    return np.stack(feats).astype(np.float32), kept


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=_REPO / "models" / "checkpoints" / "xlsr_aasist" / "aasist-v1.npz",
    )
    parser.add_argument("--experiment-id", default="baseline_v1")
    args = parser.parse_args()

    rows = _load_manifest(args.corpus)
    X, kept = _embed_corpus(args.corpus, rows)
    splits = np.asarray([str(r.get("split", "train")) for r in kept])
    langs = np.asarray([str(r.get("language", "hi")) for r in kept])
    conds = np.asarray([str(r.get("compression_status", "clean")) for r in kept])
    labels = np.asarray([1 if str(r.get("label")) == "fake" else 0 for r in kept])

    clf = AASISTClassifier()
    clf.load(args.checkpoint)
    logits = clf.predict_batch(X)

    val_mask = splits == "val"
    test_mask = splits == "test"

    audit = run_calibration_audit(
        logits[val_mask],
        labels[val_mask],
        logits[test_mask],
        labels[test_mask],
        langs[val_mask],
        conds[val_mask],
        langs[test_mask],
        conds[test_mask],
    )
    dest = _REPO / "artifacts" / "experiments" / "rq4_calibration"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "metrics.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    pred_rows: list[dict[str, object]] = []
    scores = 1.0 / (1.0 + np.exp(-np.clip(logits[:, 1] - logits[:, 0], -20, 20)))
    for row, score, label, split in zip(kept, scores.tolist(), labels.tolist(), splits.tolist(), strict=True):
        pred_rows.append(
            {
                "clip_id": row.get("clip_id"),
                "split": split,
                "language": row.get("language"),
                "label": label,
                "score_fake": round(float(score), 6),
                "source": row.get("source"),
                "compression_status": row.get("compression_status"),
            }
        )
    csv_path = write_predictions_csv(_REPO, args.experiment_id, pred_rows)
    print(json.dumps({"calibration_audit": audit, "predictions_csv": str(csv_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
