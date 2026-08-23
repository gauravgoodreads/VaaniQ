"""Training callbacks: early stopping + checkpointing (ROADMAP-030)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import structlog

log = structlog.get_logger(__name__)


class Checkpointable(Protocol):
    """Objects that can save weights to a path."""

    def save(self, path: Path) -> None:
        """Persist weights."""


class TrainingCallback:
    """Base training callback (ROADMAP-030)."""

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Handle end-of-epoch metrics.

        Args:
            epoch: Zero-based epoch index.
            metrics: Metric name → value.
        """
        log.info("epoch_end", epoch=epoch, **metrics)


class EarlyStoppingCallback(TrainingCallback):
    """Stop when monitored metric stops improving.

    # ASSUMPTION: OQ-014 - patience/mode provisional until locked from AASIST defaults.
    """

    def __init__(
        self,
        *,
        monitor: str = "val_loss",
        patience: int = 10,
        mode: str = "min",
    ) -> None:
        """Configure early stopping."""
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.best: float | None = None
        self.bad_epochs = 0
        self.should_stop = False

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Update patience counter."""
        if self.monitor not in metrics:
            return
        value = metrics[self.monitor]
        improved = False
        if (
            self.best is None
            or (self.mode == "min" and value < self.best)
            or (self.mode == "max" and value > self.best)
        ):
            improved = True
        if improved:
            self.best = value
            self.bad_epochs = 0
        else:
            self.bad_epochs += 1
            if self.bad_epochs >= self.patience:
                self.should_stop = True
                log.info("early_stopping", epoch=epoch, monitor=self.monitor, best=self.best)


class CheckpointCallback(TrainingCallback):
    """Write checkpoint each epoch and keep best."""

    def __init__(self, model: Checkpointable, directory: Path, monitor: str = "val_loss") -> None:
        """Bind model and checkpoint directory."""
        self._model = model
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
        self.best: float | None = None
        self.best_path = self._directory / "best.npz"
        self.last_path = self._directory / "last.npz"

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Save last and optionally best checkpoint."""
        self._model.save(self.last_path)
        if self.monitor in metrics:
            value = metrics[self.monitor]
            if self.best is None or value < self.best:
                self.best = value
                self._model.save(self.best_path)
                log.info("best_checkpoint", epoch=epoch, path=str(self.best_path), value=value)


class CompositeCallback(TrainingCallback):
    """Fan-out to multiple callbacks."""

    def __init__(self, callbacks: list[TrainingCallback]) -> None:
        """Store child callbacks."""
        self._callbacks = callbacks

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Dispatch to children."""
        for cb in self._callbacks:
            cb.on_epoch_end(epoch, metrics)

    @property
    def early_stopping(self) -> EarlyStoppingCallback | None:
        """Return early-stopping child if present."""
        for cb in self._callbacks:
            if isinstance(cb, EarlyStoppingCallback):
                return cb
        return None
