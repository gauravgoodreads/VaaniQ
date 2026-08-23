"""Publication figure bundle (Phase 4 / O8 / ROADMAP-041)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from vaaniq.evaluation.metrics.core import confusion_matrix, roc_curve
from vaaniq.research.figures import write_confusion_svg, write_csv, write_roc_svg


def write_publication_bundle(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    destination: Path,
    caption_prefix: str = "Fig.",
) -> dict[str, Any]:
    """Write ROC, confusion matrix, and CSV suitable for dissertation inclusion.

    Args:
        scores: Fake-class scores.
        labels: Binary labels (1=fake).
        destination: Output directory.
        caption_prefix: Caption stem.

    Returns:
        Paths and AUC.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    fpr, tpr, auc = roc_curve(scores, labels)
    cm = confusion_matrix(scores, labels)
    roc_path = write_roc_svg(
        destination / "roc.svg",
        fpr=fpr,
        tpr=tpr,
        auc=auc,
        caption=f"{caption_prefix} ROC on the logged scores. Vector SVG.",
    )
    cm_path = write_confusion_svg(
        destination / "confusion.svg",
        cm,
        title="Confusion matrix",
        caption=f"{caption_prefix} Confusion at threshold 0.5 (TN/FP/FN/TP).",
    )
    csv_path = write_csv(
        destination / "publication_scores.csv",
        ["score", "label"],
        [[s, y] for s, y in zip(scores, labels, strict=True)],
    )
    return {
        "roc_svg": str(roc_path),
        "confusion_svg": str(cm_path),
        "csv": str(csv_path),
        "auc": auc,
        "confusion": cm,
    }
