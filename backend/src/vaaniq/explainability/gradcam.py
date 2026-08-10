"""Grad-CAM explainer stub (ROADMAP-049 / REQ-075)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.domain.entities import ClipMetadata, ExplanationArtefact, Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.explainer import Explainer


class GradCamExplainer(Explainer):
    """Temporal Grad-CAM heatmap explainer.

    TODO(ROADMAP-049): produce ExplanationArtefact heatmap URIs (OQ-034).
    """

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Explain decision (deferred to ROADMAP-049)."""
        raise NotImplementedInPhaseError("ROADMAP-049", "GradCamExplainer.explain")
