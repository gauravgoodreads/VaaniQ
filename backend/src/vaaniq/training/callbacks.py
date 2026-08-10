"""Training callback stubs (ROADMAP-030)."""

from __future__ import annotations

from vaaniq.core.errors import NotImplementedInPhaseError


class TrainingCallback:
    """Hook into trainer lifecycle events.

    TODO(ROADMAP-030): early stopping, checkpointing, metric logging.
    """

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Handle end-of-epoch (deferred to ROADMAP-030)."""
        raise NotImplementedInPhaseError("ROADMAP-030", "TrainingCallback.on_epoch_end")
