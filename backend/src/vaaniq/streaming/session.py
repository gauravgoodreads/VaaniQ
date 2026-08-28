"""Streaming session manager (ROADMAP-055 / REQ-096)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import structlog

from vaaniq.core.domain.entities import Embedding, PredictionResult, Probabilities, Waveform
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.types import CompressionCondition, Label, Language, ReliabilityLevel
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.streaming.window_buffer import WindowBuffer

log = structlog.get_logger(__name__)

# Live mic is noisy / OOD vs studio clips: require stronger fake evidence.
_LIVE_FAKE_THRESHOLD = 0.85
_MIN_RMS = 0.012
# Need two consecutive strong-fake windows before emitting FAKE (stops flicker).
_FAKE_STREAK = 2


@dataclass
class StreamingSession:
    """Bind a window buffer to optional live inference."""

    session_id: str
    buffer: WindowBuffer = field(default_factory=WindowBuffer)
    classifier: Classifier | None = None
    language: Language = Language.HI
    predictions: list[PredictionResult] = field(default_factory=list)
    _fake_streak: int = 0

    def ingest(self, chunk: bytes) -> list[PredictionResult]:
        """Ingest PCM16 LE chunk and run inference on completed windows."""
        windows = self.buffer.push(chunk)
        results: list[PredictionResult] = []
        for wav in windows:
            if self.classifier is None:
                continue
            result = self._score_window(wav)
            if result is None:
                continue
            self.predictions.append(result)
            results.append(result)
        log.info("stream_ingest", session_id=self.session_id, n_windows=len(windows))
        return results

    def _score_window(self, wav: Waveform) -> PredictionResult | None:
        samples = np.asarray(wav.samples, dtype=np.float32).reshape(-1)
        if samples.size == 0:
            return None
        rms = float(np.sqrt(np.mean(np.square(samples))))
        # Skip near-silence / keyboard bumps (often mis-fired as fake).
        if rms < _MIN_RMS:
            return None

        assert self.classifier is not None
        vec = acoustic_embedding(wav, dim=int(getattr(self.classifier, "input_dim", 1024)))
        emb = Embedding(
            vector=vec,
            model_id="stream-acoustic",
            clip_id=f"{self.session_id}-{len(self.predictions)}",
        )
        logits = self.classifier.predict(emb)
        probs = _softmax(logits.values)
        fake_p = float(probs[1])

        # Mic-speech prior: natural energy dynamics nudge toward real.
        hop = max(1, int(wav.sample_rate_hz * 0.02))
        if samples.size >= hop * 8:
            frames = samples[: samples.size - (samples.size % hop)].reshape(-1, hop)
            energies = np.mean(np.square(frames), axis=1)
            dyn = float(np.std(energies) / (np.mean(energies) + 1e-8))
            if dyn > 0.35:
                fake_p = max(0.0, fake_p - 0.18)
            # Extra room-noise cue (typical laptop mic, rare in clean TTS).
            noise_floor = float(np.percentile(energies, 10))
            if noise_floor > 1e-5:
                fake_p = max(0.0, fake_p - 0.08)

        strong_fake = fake_p >= _LIVE_FAKE_THRESHOLD
        if strong_fake:
            self._fake_streak += 1
        else:
            self._fake_streak = 0
        label = Label.FAKE if self._fake_streak >= _FAKE_STREAK else Label.REAL
        raw_conf = max(fake_p, 1.0 - fake_p)
        conf = round(float(np.clip(0.67 + (raw_conf - 0.52) * 0.22 / 0.45, 0.67, 0.89)), 3)
        reliability = (
            ReliabilityLevel.HIGH
            if conf >= 0.85
            else ReliabilityLevel.MODERATE
            if conf >= 0.65
            else ReliabilityLevel.LOW
        )
        return PredictionResult(
            label=label,
            confidence=conf,
            reliability=reliability,
            language=self.language,
            compression_status=CompressionCondition.CLEAN,
            probabilities=Probabilities(values=probs, class_order=logits.class_order),
        )

    def finalize(self) -> list[PredictionResult]:
        """Finalize session and return accumulated predictions."""
        log.info("stream_finalize", session_id=self.session_id, n=len(self.predictions))
        return list(self.predictions)


def _softmax(values: np.ndarray) -> np.ndarray:
    z = values - np.max(values)
    ex = np.exp(z)
    return np.asarray(ex / np.sum(ex), dtype=np.float32)
