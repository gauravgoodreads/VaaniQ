"""RawNet2 baseline stub (ROADMAP-032 / REQ-043)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Embedding, Logits
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.classifier import Classifier


class RawNet2Classifier(Classifier):
    """RawNet2 baseline classifier.

    TODO(ROADMAP-032): adapt raw-waveform path to Classifier port or extend port.
    """

    def predict(self, emb: Embedding) -> Logits:
        """Predict logits (deferred to ROADMAP-032)."""
        raise NotImplementedInPhaseError("ROADMAP-032", "RawNet2Classifier.predict")
