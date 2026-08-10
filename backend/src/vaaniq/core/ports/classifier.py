"""Classifier port (REQ-038, REQ-042, REQ-043)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vaaniq.core.domain.entities import Embedding, Logits


class Classifier(ABC):
    """Map embeddings (or waveforms, for raw baselines) to logits.

    Serves REQ-038 (AASIST), REQ-042 (LFCC-GMM), REQ-043 (RawNet2).
    Implementations land in ROADMAP-029-032.
    """

    @abstractmethod
    def predict(self, emb: Embedding) -> Logits:
        """Predict class logits from ``emb``.

        Args:
            emb: Cached or freshly extracted embedding.

        Returns:
            Raw logits in ``Label`` class order.
        """
