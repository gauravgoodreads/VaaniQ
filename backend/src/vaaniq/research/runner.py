"""Offline RQ suite runner on synthetic embeddings (CI-safe)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from vaaniq.core.domain.entities import Logits
from vaaniq.core.types import Language
from vaaniq.research.calibration_study import run_calibration_suite
from vaaniq.research.compression_study import run_compression_suite
from vaaniq.research.cross_lingual import run_cross_lingual_suite
from vaaniq.research.error_analysis import analyze_errors
from vaaniq.research.publication import write_publication_bundle
from vaaniq.research.reports import ResearchReportBundle
from vaaniq.research.store import ExperimentStore


def run_fixture_suites(root: Path, *, seed: int = 42) -> dict[str, Any]:
    """Run RQ1/RQ3/RQ4 software paths on synthetic data (no network, no GPU).

    Real curated-hour results remain operator-side after HF ingest (OQ-002).
    """
    root = Path(root)
    rng = np.random.default_rng(seed)
    embs: dict[Language, tuple[NDArray[np.float32], NDArray[np.int64]]] = {}
    for lang in Language:
        x = rng.normal(0, 1, size=(24, 1024)).astype(np.float32)
        y = np.array([i % 2 for i in range(24)], dtype=np.int64)
        embs[lang] = (x, y)
    store = ExperimentStore(root=root / "experiments")
    xl = run_cross_lingual_suite(
        embs, store=store, output_dir=root / "figures" / "cross_lingual", seed=seed, max_epochs=1
    )
    scores = {
        "clean": ([0.1, 0.2, 0.85, 0.9], [0, 0, 1, 1]),
        "opus_16kbps": ([0.2, 0.25, 0.7, 0.8], [0, 0, 1, 1]),
        "opus_whatsapp_sim": ([0.22, 0.3, 0.65, 0.78], [0, 0, 1, 1]),
    }
    compress = run_compression_suite(
        scores, store=store, output_dir=root / "figures" / "compression", seed=seed
    )
    logits = [
        Logits(values=np.array([2.0, 0.1], dtype=np.float32)),
        Logits(values=np.array([0.1, 2.0], dtype=np.float32)),
    ] * 6
    labels = [0, 1] * 6
    calib = run_calibration_suite(
        logits, labels, store=store, output_dir=root / "figures" / "calibration", seed=seed
    )
    pub = write_publication_bundle(
        [0.1, 0.2, 0.8, 0.9],
        [0, 0, 1, 1],
        destination=root / "figures" / "publication",
        caption_prefix="Fig. demo",
    )
    err_rows = [
        {
            "clip_id": "a",
            "language": "hi",
            "condition": "clean",
            "attack_type": "tts",
            "score": 0.9,
            "label": 0,
            "confidence": 0.9,
            "pred": 1,
        },
        {
            "clip_id": "b",
            "language": "ta",
            "condition": "opus_16kbps",
            "attack_type": "voice_clone",
            "score": 0.2,
            "label": 1,
            "confidence": 0.52,
            "pred": 0,
        },
    ]
    errors = analyze_errors(err_rows, destination=root / "reports" / "error_analysis.md")
    reports = ResearchReportBundle(root / "reports").write_all(
        experiment_id="fixture-suites",
        eval_payload={"metrics": {"eer": 0.25}, "matrices": xl["matrix"], "slices": {}},
        calibration={"ece": calib["ece_temperature"]},
        experiments={"n": len(store.list_records())},
        dataset={"total_clips": 0},
        model={"name": "aasist-v1"},
        human={"n_responses": 0},
        explain={"artefacts": 0},
        figures=[str(calib["reliability_svg"]), str(compress["svg"]), str(xl["svg"])],
    )
    return {
        "cross_lingual": xl,
        "compression": compress,
        "calibration": calib,
        "publication": pub,
        "errors": errors,
        "reports": {k: str(v) for k, v in reports.items()},
    }
