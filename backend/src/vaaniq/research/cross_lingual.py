"""Leave-one-language-out experiments (RQ3 / O4 / ROADMAP-038)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from vaaniq.core.types import Language
from vaaniq.evaluation.metrics.core import (
    bootstrap_metric_ci,
    equal_error_rate,
    min_dcf,
)
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.research.figures import write_csv, write_heatmap_svg
from vaaniq.research.records import ResearchRunRecord
from vaaniq.research.store import ExperimentStore, collect_hardware

Float32Array = NDArray[np.float32]


def leave_one_language_folds() -> list[dict[str, Any]]:
    """Return HI/MR/TA leave-one-out folds (proposal p.6 train-2/test-1)."""
    langs = list(Language)
    folds: list[dict[str, Any]] = []
    for held in langs:
        train = [lang for lang in langs if lang != held]
        folds.append(
            {
                "name": f"train_{train[0].value}_{train[1].value}_test_{held.value}",
                "train": train,
                "test": held,
            }
        )
    return folds


def run_cross_lingual_suite(
    embeddings: Mapping[Language, tuple[Float32Array, NDArray[np.int64]]],
    *,
    store: ExperimentStore,
    output_dir: Path,
    seed: int = 42,
    max_epochs: int = 4,
    dataset_version: str = "fixtures",
) -> dict[str, Any]:
    """Train on two languages, test on the held-out language (RQ3).

    Args:
        embeddings: Per-language ``(features [N,D], labels [N])``.
        store: Experiment catalogue.
        output_dir: CSV/SVG destination.
        seed: RNG seed.
        max_epochs: AASIST NumPy epochs. # ASSUMPTION: OQ-014
        dataset_version: Dataset checksum/version string.

    Returns:
        Matrix plus table path metadata.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix: dict[str, dict[str, float]] = {
        a.value: {b.value: float("nan") for b in Language} for a in Language
    }
    rows: list[list[object]] = []
    for fold in leave_one_language_folds():
        train_langs: Sequence[Language] = fold["train"]
        test_lang: Language = fold["test"]
        x_tr = np.concatenate([embeddings[lang][0] for lang in train_langs], axis=0)
        y_tr = np.concatenate([embeddings[lang][1] for lang in train_langs], axis=0)
        x_te, y_te = embeddings[test_lang]
        clf = AASISTClassifier(rng=np.random.default_rng(seed))
        for _ in range(max_epochs):
            clf.train_numpy_epoch(x_tr, y_tr, learning_rate=0.01, batch_size=8)
        logits = clf.predict_batch(x_te)
        scores = logits[:, 1].tolist()
        labels = y_te.astype(int).tolist()
        eer = equal_error_rate(scores, labels)
        mdcf = min_dcf(scores, labels)
        eer_pt, eer_lo, eer_hi = bootstrap_metric_ci(
            scores, labels, metric="eer", n_samples=32, seed=seed
        )
        train_key = "+".join(lang.value for lang in train_langs)
        matrix[train_langs[0].value][test_lang.value] = eer
        rows.append([fold["name"], train_key, test_lang.value, eer, mdcf, eer_lo, eer_hi])
        rec = ResearchRunRecord(
            experiment_id=fold["name"],
            timestamp=store.now_iso(),
            git_sha=store.git_sha(),
            model_version="aasist-v1",
            dataset_version=dataset_version,
            languages=tuple(lang.value for lang in [*train_langs, test_lang]),
            compression_settings="clean",
            hyperparameters={"max_epochs": str(max_epochs), "seed": str(seed)},
            metrics={"eer": eer, "min_dcf": mdcf, "eer_ci_lo": eer_lo, "eer_ci_hi": eer_hi},
            calibration_results={},
            hardware=collect_hardware(),
            seed=seed,
            training_duration_sec=0.0,
            rq_ids=("RQ3",),
            notes="leave-one-language-out",
            extras={"eer_point": eer_pt},
        )
        store.put(rec)
    csv_path = write_csv(
        output_dir / "cross_lingual.csv",
        ["fold", "train", "test", "eer", "min_dcf", "eer_ci_lo", "eer_ci_hi"],
        rows,
    )
    svg_path = write_heatmap_svg(
        output_dir / "cross_lingual_heatmap.svg",
        matrix=matrix,
        title="Cross-lingual EER (train language row, test column)",
        caption="Fig. RQ3. Leave-one-language-out EER. Lower is better.",
    )
    return {"matrix": matrix, "csv": str(csv_path), "svg": str(svg_path), "rows": rows}
