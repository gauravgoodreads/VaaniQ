"""Calibration study runner (RQ4 / O5 / ROADMAP-043-047)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from vaaniq.calibration.ece import (
    brier_score,
    coverage_accuracy_curve,
    expected_calibration_error,
    reliability_diagram,
)
from vaaniq.calibration.temperature import TemperatureScaler
from vaaniq.core.domain.entities import Logits
from vaaniq.core.types import CompressionCondition, Language
from vaaniq.research.figures import write_csv, write_line_svg
from vaaniq.research.records import ResearchRunRecord
from vaaniq.research.store import ExperimentStore, collect_hardware


def _softmax(values: np.ndarray) -> np.ndarray:
    z = values - np.max(values, axis=-1, keepdims=True)
    ex = np.exp(z)
    denom = np.sum(ex, axis=-1, keepdims=True)
    return np.asarray(ex / denom, dtype=np.float64)


def run_calibration_suite(
    logits: Sequence[Logits],
    labels: Sequence[int],
    *,
    store: ExperimentStore,
    output_dir: Path,
    language: Language = Language.HI,
    condition: CompressionCondition = CompressionCondition.CLEAN,
    seed: int = 42,
) -> dict[str, Any]:
    """Compare raw vs temperature vs per-language vs per-condition (RQ4).

    Per-language and per-condition variants share the same scaler API
    (OQ-031); this runner logs them as named cells.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    y = list(labels)
    n = len(logits)
    if n >= 4:
        cut = n // 2
        fit_logits: Sequence[Logits] = list(logits)[:cut]
        fit_y = y[:cut]
        eval_logits: Sequence[Logits] = list(logits)[cut:]
        eval_y = y[cut:]
    else:
        fit_logits, fit_y = logits, y
        eval_logits, eval_y = logits, y

    eval_stacked = np.stack(
        [np.asarray(item.values, dtype=np.float32) for item in eval_logits],
        axis=0,
    )
    eval_raw = _softmax(eval_stacked)
    eval_fake_p = eval_raw[:, 1].tolist()
    eval_pred = [1 if p >= 0.5 else 0 for p in eval_fake_p]
    eval_correct = [int(a == b) for a, b in zip(eval_pred, eval_y, strict=True)]
    eval_conf = [max(p, 1.0 - p) for p in eval_fake_p]

    scaler = TemperatureScaler()
    scaler.fit(fit_logits, fit_y, language=language, condition=condition)
    cal_p: list[float] = []
    for item in eval_logits:
        probs = scaler.transform(item, language=language, condition=condition)
        cal_p.append(float(probs.values[1]))
    cal_pred = [1 if p >= 0.5 else 0 for p in cal_p]
    cal_corr = [int(a == b) for a, b in zip(cal_pred, eval_y, strict=True)]
    cal_conf = [max(p, 1.0 - p) for p in cal_p]

    cells = {
        "raw": (eval_conf, eval_correct, eval_fake_p),
        "temperature": (cal_conf, cal_corr, cal_p),
        f"per_language_{language.value}": (cal_conf, cal_corr, cal_p),
        f"per_condition_{condition.value}": (cal_conf, cal_corr, cal_p),
    }
    rows: list[list[object]] = []
    for name, (c, corr, pos) in cells.items():
        ece = expected_calibration_error(c, corr)
        brier = brier_score(pos, eval_y)
        rows.append([name, ece, brier])
        store.put(
            ResearchRunRecord(
                experiment_id=f"calib_{name}",
                timestamp=store.now_iso(),
                git_sha=store.git_sha(),
                model_version="aasist-v1",
                dataset_version="fixtures",
                languages=(language.value,),
                compression_settings=condition.value,
                hyperparameters={"seed": str(seed)},
                metrics={},
                calibration_results={"ece": ece, "brier": brier},
                hardware=collect_hardware(),
                seed=seed,
                training_duration_sec=0.0,
                rq_ids=("RQ4",),
            )
        )
    csv_path = write_csv(output_dir / "calibration_cells.csv", ["cell", "ece", "brier"], rows)
    diagram = reliability_diagram(cal_conf, cal_corr)
    svg_path = write_line_svg(
        output_dir / "reliability_diagram.svg",
        xs=[d["confidence"] for d in diagram],
        ys=[d["accuracy"] for d in diagram],
        title="Reliability diagram (temperature scaled)",
        xlabel="Confidence",
        ylabel="Accuracy",
        caption="Fig. RQ4. Reliability diagram after temperature scaling (OQ-017, 15 bins).",
    )
    cov = coverage_accuracy_curve(cal_conf, cal_corr)
    cov_svg = write_line_svg(
        output_dir / "coverage_curve.svg",
        xs=[d["coverage"] for d in cov],
        ys=[d["accuracy"] for d in cov],
        title="Coverage vs accuracy",
        xlabel="Coverage",
        ylabel="Accuracy",
        caption="Fig. RQ4. Coverage-accuracy curve (REQ-061).",
    )
    hist_xs = list(range(10))
    hist_ys = [float(sum(1 for c in cal_conf if i / 10 <= c < (i + 1) / 10)) for i in range(10)]
    hist_svg = write_line_svg(
        output_dir / "confidence_histogram.svg",
        xs=[float(x) for x in hist_xs],
        ys=hist_ys,
        title="Confidence histogram",
        xlabel="Bin",
        ylabel="Count",
        caption="Fig. RQ4. Histogram of max-class confidence after calibration.",
    )
    ece_raw = rows[0][1]
    ece_t = rows[1][1]
    return {
        "csv": str(csv_path),
        "reliability_svg": str(svg_path),
        "coverage_svg": str(cov_svg),
        "histogram_svg": str(hist_svg),
        "rows": rows,
        "ece_raw": float(ece_raw) if isinstance(ece_raw, int | float) else 0.0,
        "ece_temperature": float(ece_t) if isinstance(ece_t, int | float) else 0.0,
        "n_fit": len(fit_y),
        "n_eval": len(eval_y),
    }
