"""LR scheduler stubs (ROADMAP-030)."""

from __future__ import annotations

from vaaniq.core.errors import NotImplementedInPhaseError


class LearningRateScheduler:
    """Learning-rate schedule interface.

    TODO(ROADMAP-030): wire config-driven schedules.
    """

    def step(self, epoch: int) -> float:
        """Return LR for ``epoch`` (deferred to ROADMAP-030)."""
        raise NotImplementedInPhaseError("ROADMAP-030", "LearningRateScheduler.step")
