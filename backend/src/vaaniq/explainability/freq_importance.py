"""Frequency-band importance stub (ROADMAP-050 / REQ-076)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.domain.entities import ClipMetadata, ExplanationArtefact, Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.explainer import Explainer


class FrequencyBandExplainer(Explainer):
    """Frequency-band ablation importance explainer.

    TODO(ROADMAP-050): band occlusion table artefact.
    """

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Explain decision (deferred to ROADMAP-050)."""
        raise NotImplementedInPhaseError("ROADMAP-050", "FrequencyBandExplainer.explain")
