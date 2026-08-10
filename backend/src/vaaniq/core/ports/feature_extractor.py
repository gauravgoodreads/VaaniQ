"""Feature extraction port (REQ-036)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vaaniq.core.domain.entities import Embedding, Waveform


class FeatureExtractor(ABC):
    """Extract frozen SSL embeddings from audio.

    Serves REQ-036, REQ-041. Implementation: FrozenXLSRExtractor (ROADMAP-025).
    Bodies raise NotImplementedError until P4.
    """

    @abstractmethod
    def extract(self, wav: Waveform, *, clip_id: str) -> Embedding:
        """Extract an embedding for ``clip_id``.

        Args:
            wav: Preprocessed waveform.
            clip_id: Stable clip identifier for cache keys.

        Returns:
            Embedding tied to the configured model id.
        """
