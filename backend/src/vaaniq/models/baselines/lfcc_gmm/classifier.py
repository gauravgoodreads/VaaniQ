"""LFCC+GMM baseline stub (ROADMAP-031 / REQ-042)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Embedding, Logits
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.classifier import Classifier


class LfccGmmClassifier(Classifier):
    """LFCC + GMM baseline classifier.

    TODO(ROADMAP-031): classical front-end + GMM scoring via Classifier port.
    """

    def predict(self, emb: Embedding) -> Logits:
        """Predict logits (deferred to ROADMAP-031)."""
        raise NotImplementedInPhaseError("ROADMAP-031", "LfccGmmClassifier.predict")
