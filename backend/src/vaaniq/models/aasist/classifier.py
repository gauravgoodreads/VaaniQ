"""AASIST classifier stub (ROADMAP-029 / REQ-038)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Embedding, Logits
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.classifier import Classifier


class AASISTClassifier(Classifier):
    """AASIST head on cached XLS-R embeddings.

    TODO(ROADMAP-029): load checkpoint and map Embedding → Logits.
    """

    def predict(self, emb: Embedding) -> Logits:
        """Predict logits (deferred to ROADMAP-029)."""
        raise NotImplementedInPhaseError("ROADMAP-029", "AASISTClassifier.predict")
