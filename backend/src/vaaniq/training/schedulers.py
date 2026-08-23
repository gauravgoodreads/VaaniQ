"""Learning-rate schedules (ROADMAP-030)."""

from __future__ import annotations


class LearningRateScheduler:
    """Step / cosine-style LR schedule.

    # ASSUMPTION: OQ-014 - schedule form provisional.
    """

    def __init__(
        self,
        base_lr: float,
        *,
        warmup_epochs: int = 0,
        decay_factor: float = 0.5,
        decay_every: int = 20,
    ) -> None:
        """Bind schedule hyperparameters."""
        self.base_lr = base_lr
        self.warmup_epochs = warmup_epochs
        self.decay_factor = decay_factor
        self.decay_every = max(1, decay_every)

    def step(self, epoch: int) -> float:
        """Return LR for ``epoch`` (0-based).

        Args:
            epoch: Current epoch index.

        Returns:
            Learning rate for this epoch.
        """
        if epoch < self.warmup_epochs:
            return self.base_lr * float(epoch + 1) / float(self.warmup_epochs)
        decays = epoch // self.decay_every
        return self.base_lr * (self.decay_factor**decays)
