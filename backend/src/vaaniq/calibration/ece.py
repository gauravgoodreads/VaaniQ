"""ECE and reliability diagram stubs (ROADMAP-044 / REQ-057-058)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.errors import NotImplementedInPhaseError


def expected_calibration_error(
    confidences: Sequence[float],
    correct: Sequence[bool],
    *,
    n_bins: int,
) -> float:
    """Compute ECE (deferred to ROADMAP-044).

    ASSUMPTION: OQ-017 — bin count comes from config, not hardcoded here.
    """
    raise NotImplementedInPhaseError("ROADMAP-044", "expected_calibration_error")
