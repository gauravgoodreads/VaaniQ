"""Automatic error analysis reports (Phase 4 / RQ1-RQ3)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from vaaniq.evaluation.metrics.core import classification_report_scores, equal_error_rate


def analyze_errors(
    rows: Sequence[dict[str, Any]],
    *,
    destination: Path | None = None,
) -> dict[str, Any]:
    """Detect worst slices and over/under-confident errors.

    Each row needs: ``language``, ``condition``, ``attack_type``, ``score``,
    ``label`` (0/1), ``confidence``, ``pred`` (0/1).
    """
    by_lang: dict[str, list[dict[str, Any]]] = {}
    by_cond: dict[str, list[dict[str, Any]]] = {}
    by_atk: dict[str, list[dict[str, Any]]] = {}
    fps: Counter[str] = Counter()
    fns: Counter[str] = Counter()
    overconfident: list[dict[str, Any]] = []
    uncertain: list[dict[str, Any]] = []
    for row in rows:
        by_lang.setdefault(str(row["language"]), []).append(row)
        by_cond.setdefault(str(row["condition"]), []).append(row)
        by_atk.setdefault(str(row.get("attack_type", "unknown")), []).append(row)
        pred = int(row["pred"])
        lab = int(row["label"])
        conf = float(row["confidence"])
        if pred == 1 and lab == 0:
            fps[str(row["language"])] += 1
        if pred == 0 and lab == 1:
            fns[str(row["language"])] += 1
        if pred != lab and conf >= 0.85:
            overconfident.append(row)
        if 0.45 <= conf <= 0.55:
            uncertain.append(row)

    def _worst(groups: dict[str, list[dict[str, Any]]]) -> str:
        worst_name = "n/a"
        worst_eer = -1.0
        for name, group in groups.items():
            eer = equal_error_rate(
                [float(r["score"]) for r in group],
                [int(r["label"]) for r in group],
            )
            if eer > worst_eer:
                worst_eer = eer
                worst_name = name
        return worst_name

    summary = {
        "worst_language": _worst(by_lang),
        "worst_compression": _worst(by_cond),
        "worst_attack_type": _worst(by_atk),
        "n_overconfident": len(overconfident),
        "n_uncertain": len(uncertain),
        "false_positives_by_language": dict(fps),
        "false_negatives_by_language": dict(fns),
        "accuracy": classification_report_scores(
            [float(r["score"]) for r in rows],
            [int(r["label"]) for r in rows],
        )["accuracy"]
        if rows
        else 0.0,
    }
    if destination is not None:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Error analysis",
            "",
            f"- Worst-performing language: **{summary['worst_language']}**",
            f"- Worst compression level: **{summary['worst_compression']}**",
            f"- Worst attack type: **{summary['worst_attack_type']}**",
            f"- Overconfident errors (conf>=0.85): {summary['n_overconfident']}",
            f"- Uncertain predictions (conf in [0.45, 0.55]): {summary['n_uncertain']}",
            f"- False positives by language: `{summary['false_positives_by_language']}`",
            f"- False negatives by language: `{summary['false_negatives_by_language']}`",
            "",
            "Limitations: slice sizes on fixture data are small; do not cite as RQ results.",
            "",
        ]
        destination.write_text("\n".join(lines), encoding="utf-8")
    return summary
