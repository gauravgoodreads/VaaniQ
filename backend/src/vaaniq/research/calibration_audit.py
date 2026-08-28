"""Extended calibration audit (RQ4 / P7).

Compares uncalibrated vs global vs per-language vs per-condition temperature
scaling using validation-only fitting and held-out test evaluation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from vaaniq.calibration.ece import brier_score, expected_calibration_error, reliability_diagram
from vaaniq.calibration.temperature import TemperatureScaler
from vaaniq.core.domain.entities import Logits
from vaaniq.core.types import CompressionCondition, Label, Language


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits, axis=1, keepdims=True)
    ex = np.exp(z)
    denom = np.sum(ex, axis=1, keepdims=True)
    return np.asarray(ex / denom, dtype=np.float64)


def _pack_calibration(
    probs: np.ndarray,
    labels: np.ndarray,
    *,
    include_diagram: bool = False,
) -> dict[str, Any]:
    pred = np.argmax(probs, axis=1)
    conf = np.max(probs, axis=1)
    correct = (pred == labels).astype(int)
    fake_p = probs[:, 1]
    out: dict[str, Any] = {
        "ece": round(expected_calibration_error(conf.tolist(), correct.tolist()), 4),
        "brier": round(brier_score(fake_p.tolist(), labels.astype(int).tolist()), 4),
        "nll": round(
            float(
                -np.mean(
                    np.log(
                        np.clip(
                            np.where(labels == 1, fake_p, 1.0 - fake_p),
                            1e-8,
                            1.0,
                        )
                    )
                )
            ),
            4,
        ),
    }
    if include_diagram:
        out["reliability_diagram"] = reliability_diagram(conf.tolist(), correct.tolist())
    return out


def _apply_global_temperature(
    val_logits: np.ndarray,
    val_labels: np.ndarray,
    eval_logits: np.ndarray,
) -> np.ndarray:
    scaler = TemperatureScaler()
    fit = [
        Logits(values=row.astype(np.float32), class_order=(Label.REAL, Label.FAKE))
        for row in val_logits
    ]
    scaler.fit(
        fit,
        val_labels.astype(int).tolist(),
        language=Language.HI,
        condition=CompressionCondition.CLEAN,
    )
    out: list[np.ndarray] = []
    for row in eval_logits:
        p = scaler.transform(
            Logits(values=row.astype(np.float32), class_order=(Label.REAL, Label.FAKE)),
            language=Language.HI,
            condition=CompressionCondition.CLEAN,
        )
        out.append(p.values)
    return np.stack(out)


def _apply_cell_temperature(
    val_logits: np.ndarray,
    val_labels: np.ndarray,
    eval_logits: np.ndarray,
    val_langs: np.ndarray,
    val_conds: np.ndarray,
    eval_langs: np.ndarray,
    eval_conds: np.ndarray,
    *,
    per_language: bool,
    per_condition: bool,
) -> np.ndarray:
    scaler = TemperatureScaler()
    val_objs = [
        Logits(values=row.astype(np.float32), class_order=(Label.REAL, Label.FAKE))
        for row in val_logits
    ]
    languages = (Language.HI, Language.MR, Language.TA) if per_language else (Language.HI,)
    conditions = (
        (CompressionCondition.CLEAN, CompressionCondition.OPUS_WHATSAPP_SIM)
        if per_condition
        else (CompressionCondition.CLEAN,)
    )
    for lang in languages:
        for cond in conditions:
            if per_language and per_condition:
                mask = (val_langs == lang.value) & (val_conds == cond.value)
            elif per_language:
                mask = val_langs == lang.value
            else:
                mask = val_conds == cond.value
            cell_logits = [obj for obj, keep in zip(val_objs, mask, strict=True) if keep]
            cell_labels = val_labels[mask].astype(int).tolist()
            if len(cell_logits) < 8:
                continue
            scaler.fit(cell_logits, cell_labels, language=lang, condition=cond)

    out: list[np.ndarray] = []
    for row, lang_raw, cond_raw in zip(eval_logits, eval_langs, eval_conds, strict=True):
        lang = Language(str(lang_raw))
        cond = CompressionCondition(str(cond_raw))
        p = scaler.transform(
            Logits(values=row.astype(np.float32), class_order=(Label.REAL, Label.FAKE)),
            language=lang if per_language else Language.HI,
            condition=cond if per_condition else CompressionCondition.CLEAN,
        )
        out.append(p.values)
    return np.stack(out)


def run_calibration_audit(
    val_logits: np.ndarray,
    val_labels: np.ndarray,
    test_logits: np.ndarray,
    test_labels: np.ndarray,
    val_langs: np.ndarray,
    val_conds: np.ndarray,
    test_langs: np.ndarray,
    test_conds: np.ndarray,
) -> dict[str, Any]:
    """Run RQ4 calibration comparison on held-out test only.

    All temperature parameters are fit on validation logits/labels only.
    """
    raw_probs = _softmax(test_logits)
    strategies: dict[str, Callable[[], np.ndarray]] = {
        "uncalibrated": lambda: raw_probs,
        "global_temperature": lambda: _apply_global_temperature(
            val_logits, val_labels, test_logits
        ),
        "per_language_temperature": lambda: _apply_cell_temperature(
            val_logits,
            val_labels,
            test_logits,
            val_langs,
            val_conds,
            test_langs,
            test_conds,
            per_language=True,
            per_condition=False,
        ),
        "per_condition_temperature": lambda: _apply_cell_temperature(
            val_logits,
            val_labels,
            test_logits,
            val_langs,
            val_conds,
            test_langs,
            test_conds,
            per_language=False,
            per_condition=True,
        ),
        "per_language_and_condition": lambda: _apply_cell_temperature(
            val_logits,
            val_labels,
            test_logits,
            val_langs,
            val_conds,
            test_langs,
            test_conds,
            per_language=True,
            per_condition=True,
        ),
    }

    rows: dict[str, dict[str, Any]] = {}
    best_ece = float("inf")
    best_name = "uncalibrated"
    for name, fn in strategies.items():
        probs = fn()
        include_diag = name == "per_language_and_condition"
        pack = _pack_calibration(probs, test_labels, include_diagram=include_diag)
        rows[name] = pack
        if float(pack["ece"]) < best_ece:
            best_ece = float(pack["ece"])
            best_name = name

    improved = best_ece < rows["uncalibrated"]["ece"]
    return {
        "experiment_id": "rq4_calibration",
        "strategies": rows,
        "best_strategy_by_test_ece": best_name,
        "calibration_improved_on_test": improved,
        "conclusion": (
            "Validation-fitted post-hoc calibration did not improve held-out calibration "
            "under the current multilingual/domain-shift setting."
            if not improved
            else f"Strategy '{best_name}' lowered test ECE vs uncalibrated."
        ),
    }
