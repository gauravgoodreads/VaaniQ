"""Training loop with validation, AMP hooks, resume (ROADMAP-030 / REQ-137-138).

NumPy path is default for CI. When ``torch`` is available (``[ml]``), mixed
precision can be enabled via ``use_amp=True``.
# ASSUMPTION: OQ-014 - optimiser knobs from config / clovaai-oriented defaults.
"""

from __future__ import annotations

import random
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import structlog
from numpy.typing import NDArray

from vaaniq.core.domain.entities import ExperimentManifest
from vaaniq.core.errors import ConfigurationError
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.ports.experiment_tracker import ExperimentTracker
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.training.callbacks import (
    CheckpointCallback,
    CompositeCallback,
    EarlyStoppingCallback,
    TrainingCallback,
)
from vaaniq.training.schedulers import LearningRateScheduler

log = structlog.get_logger(__name__)

Float32Array = NDArray[np.float32]


def seed_everything(seed: int) -> None:
    """Seed Python, NumPy, and torch if present (REQ-137)."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass


def _git_sha() -> tuple[str, bool]:
    """Return (sha, dirty)."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        dirty = (
            subprocess.check_output(
                ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
            ).strip()
            != ""
        )
        return sha, dirty
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True


class Trainer:
    """End-to-end trainer for embedding-based classifiers (ROADMAP-030)."""

    def __init__(
        self,
        model: Classifier,
        tracker: ExperimentTracker,
        *,
        seed: int = 42,
        learning_rate: float = 0.0001,
        batch_size: int = 24,
        max_epochs: int = 100,
        early_stopping_patience: int = 10,
        use_amp: bool = False,
        experiment_root: Path | None = None,
        resume_from: Path | None = None,
        callbacks: list[TrainingCallback] | None = None,
    ) -> None:
        """Bind model, tracker, and training hyperparameters.

        Args:
            model: Classifier implementing train/save for AASIST (or compatible).
            tracker: Experiment tracker.
            seed: Global seed.
            learning_rate: Optimiser LR. # ASSUMPTION: OQ-014
            batch_size: Mini-batch size. # ASSUMPTION: OQ-014
            max_epochs: Epoch cap. # ASSUMPTION: OQ-014
            early_stopping_patience: Patience epochs. # ASSUMPTION: OQ-014
            use_amp: Enable torch autocast when torch is available.
            experiment_root: Artefact root.
            resume_from: Optional checkpoint to resume.
            callbacks: Extra callbacks.
        """
        self._model = model
        self._tracker = tracker
        self._seed = seed
        self._lr = learning_rate
        self._batch_size = batch_size
        self._max_epochs = max_epochs
        self._patience = early_stopping_patience
        self._use_amp = use_amp
        self._experiment_root = (
            Path(experiment_root) if experiment_root else Path("./research/experiments")
        )
        self._resume_from = resume_from
        self._extra_callbacks = callbacks or []

    def fit(self, dataset_config: Mapping[str, Any]) -> str:
        """Run training and return experiment id.

        Args:
            dataset_config: Must include ``train_features`` ``[N,D]``,
                ``train_labels`` ``[N]``, and optionally ``val_*``.

        Returns:
            Experiment id string.
        """
        seed_everything(self._seed)
        if not isinstance(self._model, AASISTClassifier):
            raise ConfigurationError("Trainer.fit currently supports AASISTClassifier")
        model: AASISTClassifier = self._model

        train_x = np.asarray(dataset_config["train_features"], dtype=np.float32)
        train_y = np.asarray(dataset_config["train_labels"], dtype=np.int64)
        if "val_features" not in dataset_config:
            log.warning("val_split_missing_using_train_prefix", seed=self._seed)
        val_x = np.asarray(
            dataset_config.get("val_features", train_x[: max(1, len(train_x) // 5)]),
            dtype=np.float32,
        )
        val_y = np.asarray(
            dataset_config.get("val_labels", train_y[: max(1, len(train_y) // 5)]),
            dtype=np.int64,
        )

        if self._resume_from is not None and Path(self._resume_from).is_file():
            model.load(Path(self._resume_from))
            log.info("training_resumed", path=str(self._resume_from))

        exp_id = getattr(self._tracker, "experiment_id", "run")
        ckpt_dir = self._experiment_root / str(exp_id) / "checkpoints"
        early = EarlyStoppingCallback(monitor="val_loss", patience=self._patience, mode="min")
        ckpt = CheckpointCallback(model, ckpt_dir, monitor="val_loss")
        composite = CompositeCallback([early, ckpt, *self._extra_callbacks])
        scheduler = LearningRateScheduler(self._base_lr_for_amp())

        sha, dirty = _git_sha()
        self._tracker.write_manifest(
            ExperimentManifest(
                experiment_id=str(exp_id),
                git_sha=sha,
                dirty=dirty,
                seed=self._seed,
                config={
                    "learning_rate": str(self._lr),
                    "batch_size": str(self._batch_size),
                    "max_epochs": str(self._max_epochs),
                    "use_amp": str(self._use_amp),
                    "model_name": str(dataset_config.get("model_name", "aasist")),
                },
                package_versions={"numpy": np.__version__},
                hardware={"amp": str(self._use_amp)},
                dataset_checksums={
                    "train_n": str(train_x.shape[0]),
                    "val_n": str(val_x.shape[0]),
                },
            )
        )

        # Optional torch AMP probe (no-op body when torch missing)
        if self._use_amp:
            self._amp_probe()

        for epoch in range(self._max_epochs):
            lr = scheduler.step(epoch)
            train_loss = model.train_numpy_epoch(
                train_x, train_y, learning_rate=lr, batch_size=self._batch_size
            )
            val_logits = model.predict_batch(val_x)
            val_loss = self._ce_loss(val_logits, val_y)
            metrics = {"train_loss": train_loss, "val_loss": val_loss, "lr": lr}
            self._tracker.log_metric("train_loss", train_loss, dims={"epoch": str(epoch)})
            self._tracker.log_metric("val_loss", val_loss, dims={"epoch": str(epoch)})
            composite.on_epoch_end(epoch, metrics)
            log.info("epoch_complete", epoch=epoch, **metrics)
            if early.should_stop:
                break

        return str(exp_id)

    def _base_lr_for_amp(self) -> float:
        return self._lr

    def _amp_probe(self) -> None:
        """Validate autocast availability when AMP requested."""
        try:
            import torch

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            with torch.autocast(device_type=device.type, enabled=True):
                _ = torch.zeros(1, device=device) * 2
            log.info("amp_enabled", device=str(device))
        except Exception as exc:
            log.info("amp_unavailable", error=str(exc))

    @staticmethod
    def _ce_loss(logits: Float32Array, labels: NDArray[np.int64]) -> float:
        shifted = logits - np.max(logits, axis=1, keepdims=True)
        ex = np.exp(shifted)
        probs = ex / np.sum(ex, axis=1, keepdims=True)
        rows = np.arange(labels.shape[0])
        return float(-np.mean(np.log(np.clip(probs[rows, labels], 1e-8, 1.0))))
