"""Cross-condition / cross-lingual matrix stubs (ROADMAP-038-039)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.types import CompressionCondition, Language


def cross_lingual_matrix(
    predictions: Sequence[Mapping[str, float]],
) -> Mapping[tuple[Language, Language], float]:
    """Build train-lang x test-lang EER matrix (deferred to ROADMAP-038)."""
    raise NotImplementedInPhaseError("ROADMAP-038", "cross_lingual_matrix")


def cross_condition_matrix(
    predictions: Sequence[Mapping[str, float]],
) -> Mapping[tuple[CompressionCondition, CompressionCondition], float]:
    """Build clean↔Opus condition matrix (deferred to ROADMAP-039)."""
    raise NotImplementedInPhaseError("ROADMAP-039", "cross_condition_matrix")
