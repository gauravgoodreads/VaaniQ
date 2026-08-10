"""Frozen XLS-R feature extractor stub (ROADMAP-025 / REQ-036)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Embedding, Waveform
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.feature_extractor import FeatureExtractor


class FrozenXLSRExtractor(FeatureExtractor):
    """Frozen wav2vec 2.0 XLS-R (300M) embedding extractor.

    TODO(ROADMAP-025): load weights, freeze encoder, return Embedding (OQ-013).
    """

    def extract(self, wav: Waveform, *, clip_id: str) -> Embedding:
        """Extract embedding for ``clip_id`` (deferred to ROADMAP-025)."""
        raise NotImplementedInPhaseError("ROADMAP-025", "FrozenXLSRExtractor.extract")
