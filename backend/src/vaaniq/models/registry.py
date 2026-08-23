"""In-memory model registry (ROADMAP-035)."""

from __future__ import annotations

from vaaniq.core.errors import ModelNotReadyError
from vaaniq.core.ports.classifier import Classifier
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.baselines.lfcc_gmm.classifier import LfccGmmClassifier
from vaaniq.models.baselines.rawnet2.classifier import RawNet2Classifier


class ModelRegistry:
    """Register and resolve classifiers by id (Architecture §8)."""

    def __init__(self) -> None:
        """Seed registry with default research models."""
        self._models: dict[str, Classifier] = {
            "aasist-v1": AASISTClassifier(),
            "lfcc-gmm-v1": LfccGmmClassifier(),
            "rawnet2-v1": RawNet2Classifier(),
            "english-xlsr-aasist-v1": AASISTClassifier(),
        }
        self._descriptions: dict[str, str] = {
            "aasist-v1": "Primary XLS-R + AASIST head (REQ-038)",
            "lfcc-gmm-v1": "LFCC + GMM baseline (REQ-042)",
            "rawnet2-v1": "RawNet2 waveform baseline (REQ-043)",
            "english-xlsr-aasist-v1": "English-only ASVspoof control (REQ-044)",
        }

    def register(self, model_id: str, classifier: Classifier, description: str = "") -> None:
        """Register or replace a classifier."""
        self._models[model_id] = classifier
        if description:
            self._descriptions[model_id] = description

    def get(self, model_id: str) -> Classifier:
        """Return a classifier for ``model_id``.

        Args:
            model_id: Registry key.

        Returns:
            Bound ``Classifier``.

        Raises:
            ModelNotReadyError: Unknown id.
        """
        try:
            return self._models[model_id]
        except KeyError as exc:
            raise ModelNotReadyError(f"unknown model_id={model_id}") from exc

    def list_ids(self) -> dict[str, str]:
        """Return model_id → description map."""
        return dict(self._descriptions)
