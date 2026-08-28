#!/usr/bin/env python3
"""Evaluate source-disjoint and generator-disjoint cells on Benchmark V2."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.core.domain.entities import Waveform
from vaaniq.evaluation.metrics.core import classification_report_scores, equal_error_rate, min_dcf, roc_curve
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.research.source_shortcut import run_source_shortcut_analysis


def _contingency(rows: list[dict[str, object]], key: str) -> dict[str, dict[str, int]]:
    table: dict[str, dict[str, int]] = {}
    for row in rows:
        src = str(row.get(key, "unknown"))
        lab = str(row.get("label", "unknown"))
        table.setdefault(src, Counter())
        table[src][lab] += 1
    return {k: dict(v) for k, v in table.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO / "data" / "benchmark_v2",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=_REPO / "models" / "checkpoints" / "xlsr_aasist" / "aasist-v1.npz",
    )
    args = parser.parse_args()

    manifest = args.corpus / "manifest.jsonl"
    if not manifest.is_file():
        raise SystemExit(f"missing manifest: {manifest}")

    rows: list[dict[str, object]] = []
    with manifest.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))

    pre = DefaultPreprocessor()
    clf = AASISTClassifier()
    clf.load(args.checkpoint)

    def eval_mask(name: str, mask: np.ndarray) -> dict[str, object]:
        X: list[np.ndarray] = []
        y: list[int] = []
        for row, keep in zip(rows, mask.tolist(), strict=True):
            if not keep:
                continue
            path = args.corpus / str(row.get("uri", ""))
            if not path.is_file():
                continue
            data, sr = sf.read(str(path), dtype="float32", always_2d=False)
            if getattr(data, "ndim", 1) > 1:
                data = np.mean(data, axis=1)
            wav = pre.transform(Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr)))
            X.append(acoustic_embedding(wav, dim=1024))
            y.append(1 if str(row.get("label")) == "fake" else 0)
        if not X:
            return {"n": 0}
        logits = clf.predict_batch(np.stack(X))
        z = logits - np.max(logits, axis=1, keepdims=True)
        ex = np.exp(z)
        probs = ex / np.sum(ex, axis=1, keepdims=True)
        scores = probs[:, 1].tolist()
        labels = y
        rep = classification_report_scores(scores, labels)
        _, _, auc = roc_curve(scores, labels)
        return {
            "n": len(y),
            "accuracy": round(rep["accuracy"], 4),
            "f1": round(rep["f1"], 4),
            "eer": round(equal_error_rate(scores, labels), 4),
            "min_dcf": round(min_dcf(scores, labels), 4),
            "roc_auc": round(auc, 4),
            "eval_name": name,
        }

    splits = np.asarray([str(r.get("split", "train")) for r in rows])
    sources = np.asarray([str(r.get("source", "unknown")) for r in rows])
    gen_buckets = np.asarray([str(r.get("generator_disjoint_bucket", "train")) for r in rows])
    test = splits == "test"

    # Source-disjoint: held-out FLEURS or Common Voice real on test split
    cv_test_real = test & (
        (sources == "common_voice") | (sources == "fleurs")
    ) & np.asarray([str(r.get("label")) == "real" for r in rows])
    kathbath_test = test & (sources == "kathbath")

    shortcut_v2 = run_source_shortcut_analysis(_REPO, manifest_path=manifest)

    independent = eval_mask("independent_real_test", cv_test_real)
    independent["status"] = "PILOT"
    independent["minimum_n_for_claim"] = 30
    independent["note"] = "No statistically useful unseen-source estimate yet; pipeline validation only."

    gen_held = eval_mask("generator_held_out_test", test & (gen_buckets == "test"))
    gen_held["status"] = "PENDING" if gen_held.get("n", 0) == 0 else "PILOT"

    payload = {
        "experiment_id": "benchmark_v2",
        "status": "PARTIAL",
        "scope": "partial_external_source_pilot",
        "source_x_label": _contingency(rows, "source"),
        "generator_x_label": _contingency(rows, "generation_model"),
        "v2_source_shortcut_warning": (
            "High source-probe accuracy means domain identity is easy to predict; "
            "this does NOT demonstrate reduced shortcut risk versus V1."
        ),
        "evaluations": {
            "full_test": eval_mask("full_test", test),
            "kathbath_test": eval_mask("kathbath_test", kathbath_test),
            "independent_real_test": independent,
            "generator_held_out_test": gen_held,
        },
        "source_shortcut_v2": shortcut_v2,
        "v1_vs_v2_shortcut_comparison_note": (
            "Compare label_probe_test_accuracy and source_probe_test_accuracy "
            "against artifacts/experiments/source_shortcut/metrics.json (V1)."
        ),
    }
    dest = _REPO / "artifacts" / "experiments" / "benchmark_v2"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
