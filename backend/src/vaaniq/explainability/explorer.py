"""Misclassified-sample explorer (Phase 4 explainability)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def misclassified_explorer(
    rows: Sequence[dict[str, Any]],
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return the highest-confidence errors for UI/report inspection.

    Each row: ``clip_id``, ``pred``, ``label``, ``confidence``, plus optional
    metadata (language, condition, attack_type).
    """
    errors = [row for row in rows if int(row["pred"]) != int(row["label"])]
    errors.sort(key=lambda r: float(r.get("confidence", 0.0)), reverse=True)
    return errors[:limit]
