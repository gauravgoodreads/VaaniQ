"""English-only XLS-R + AASIST control baseline (ROADMAP-033 / REQ-044).

Trains the same AASIST head on an English ASVspoof-style embedding cache
configured via ``configs/train/english_only.yaml``.
# ASSUMPTION: OQ-015 - ASVspoof 2019 LA train subset.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from vaaniq.config.domains import TrainEnglishOnlyConfig, XlsrAasistConfig
from vaaniq.models.aasist.classifier import AASISTClassifier

if TYPE_CHECKING:
    from vaaniq.training.trainer import Trainer

log = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class EnglishOnlyBaselineResult:
    """Artefacts from an English-only control run."""

    experiment_id: str
    checkpoint_path: Path
    asvspoof_subset: str


class EnglishOnlyXlsrAasistBaseline:
    """RQ2 English-only control using shared AASIST head (REQ-044)."""

    def __init__(
        self,
        train_config: TrainEnglishOnlyConfig,
        model_config: XlsrAasistConfig | None = None,
        *,
        trainer: Trainer | None = None,
    ) -> None:
        """Bind English-only train config and optional trainer."""
        self._train_config = train_config
        self._model_config = model_config or XlsrAasistConfig()
        self._classifier = AASISTClassifier(self._model_config)
        self._trainer = trainer

    @property
    def classifier(self) -> AASISTClassifier:
        """Return the underlying AASIST classifier."""
        return self._classifier

    def run(self, dataset: dict[str, Any]) -> EnglishOnlyBaselineResult:
        """Train on English embeddings supplied in ``dataset``.

        Args:
            dataset: Mapping with ``train_features``, ``train_labels``,
                ``val_features``, ``val_labels`` (same contract as ``Trainer.fit``).

        Returns:
            Experiment id and checkpoint path.
        """
        # ASSUMPTION: OQ-015
        log.info(
            "english_only_baseline_start",
            subset=self._train_config.asvspoof_subset,
            split=self._train_config.asvspoof_split,
        )
        if self._trainer is None:
            from vaaniq.training.tracker import FileExperimentTracker
            from vaaniq.training.trainer import Trainer

            self._trainer = Trainer(
                self._classifier,
                FileExperimentTracker(root=self._train_config.experiment_root),
                seed=self._train_config.seed,
                learning_rate=self._train_config.learning_rate,
                batch_size=self._train_config.batch_size,
                max_epochs=self._train_config.max_epochs,
                experiment_root=self._train_config.experiment_root,
            )
        exp_id = self._trainer.fit(
            {
                **dataset,
                "model_name": "english_only_xlsr_aasist",
                "asvspoof_subset": self._train_config.asvspoof_subset,
            }
        )
        ckpt = Path(self._train_config.experiment_root) / exp_id / "checkpoints" / "best.npz"
        return EnglishOnlyBaselineResult(
            experiment_id=exp_id,
            checkpoint_path=ckpt,
            asvspoof_subset=self._train_config.asvspoof_subset,
        )
