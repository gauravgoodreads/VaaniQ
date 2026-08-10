"""Training loop stub (ROADMAP-030 / REQ-137-138)."""

from __future__ import annotations

from collections.abc import Mapping

from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.ports.experiment_tracker import ExperimentTracker


class Trainer:
    """Seeded training loop with run manifests.

    TODO(ROADMAP-030): seed random/numpy/torch; write ExperimentManifest.
    """

    def __init__(
        self,
        classifier: Classifier,
        tracker: ExperimentTracker,
        *,
        seed: int,
    ) -> None:
        """Bind classifier, tracker, and seed."""
        self._classifier = classifier
        self._tracker = tracker
        self._seed = seed

    def fit(self, train_cfg: Mapping[str, str]) -> str:
        """Run training and return experiment id (deferred to ROADMAP-030)."""
        raise NotImplementedInPhaseError("ROADMAP-030", "Trainer.fit")
