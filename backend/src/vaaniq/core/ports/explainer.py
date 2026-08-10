"""Explainability port (REQ-075, REQ-076)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from vaaniq.core.domain.entities import ClipMetadata, ExplanationArtefact, Waveform


class Explainer(ABC):
    """Produce explainability artefacts for a clip.

    Serves REQ-075 (Grad-CAM), REQ-076 (frequency-band importance),
    REQ-077-078. Implementations: ROADMAP-049-052.
    """

    @abstractmethod
    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Explain a model decision for ``clip``.

        Args:
            clip: Clip metadata.
            wav: Waveform used at inference.
            model_id: Registry id of the model being explained.

        Returns:
            One or more artefacts (heatmap, band table, spectrogram, etc.).
        """
