"""Streaming session manager (ROADMAP-055 / REQ-096)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import structlog

from vaaniq.core.domain.entities import Embedding, PredictionResult, Probabilities
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.types import CompressionCondition, Label, Language, ReliabilityLevel
from vaaniq.streaming.window_buffer import WindowBuffer

log = structlog.get_logger(__name__)


@dataclass
class StreamingSession:
    """Bind a window buffer to optional live inference."""

    session_id: str
    buffer: WindowBuffer = field(default_factory=WindowBuffer)
    classifier: Classifier | None = None
    language: Language = Language.HI
    predictions: list[PredictionResult] = field(default_factory=list)

    def ingest(self, chunk: bytes) -> list[PredictionResult]:
        """Ingest audio chunk and run inference on completed windows."""
        windows = self.buffer.push(chunk)
        results: list[PredictionResult] = []
        for wav in windows:
            if self.classifier is None:
                continue
            emb = Embedding(
                vector=np.asarray(wav.samples, dtype=np.float32),
                model_id="stream",
                clip_id=f"{self.session_id}-{len(self.predictions)}",
            )
            # AASIST expects fixed dim - use mean-pool stats embedding for stream path
            if hasattr(self.classifier, "input_dim"):
                dim = int(self.classifier.input_dim)
                vec = np.zeros(dim, dtype=np.float32)
                flat = emb.vector.reshape(-1)
                n = min(dim, flat.size)
                vec[:n] = flat[:n]
                emb = Embedding(vector=vec, model_id="stream", clip_id=emb.clip_id)
            logits = self.classifier.predict(emb)
            probs = _softmax(logits.values)
            fake_p = float(probs[1])
            label = Label.FAKE if fake_p >= 0.5 else Label.REAL
            conf = max(fake_p, 1.0 - fake_p)
            result = PredictionResult(
                label=label,
                confidence=conf,
                reliability=ReliabilityLevel.MODERATE,
                language=self.language,
                compression_status=CompressionCondition.CLEAN,
                probabilities=Probabilities(values=probs, class_order=logits.class_order),
            )
            self.predictions.append(result)
            results.append(result)
        log.info("stream_ingest", session_id=self.session_id, n_windows=len(windows))
        return results

    def finalize(self) -> list[PredictionResult]:
        """Finalize session and return accumulated predictions."""
        log.info("stream_finalize", session_id=self.session_id, n=len(self.predictions))
        return list(self.predictions)


def _softmax(values: np.ndarray) -> np.ndarray:
    z = values - np.max(values)
    ex = np.exp(z)
    return np.asarray(ex / np.sum(ex), dtype=np.float32)
