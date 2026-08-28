"""RawNet2-style approximate baseline (ROADMAP-032 / REQ-043).

Lightweight raw-waveform CNN approximating RawNet2 for CI without GPU.
Accepts waveforms via ``predict_waveform``; ``predict`` treats
``Embedding.vector`` as mono PCM samples (documented contract for the
Classifier port).
# ASSUMPTION: OQ-014 - lr/batch/epochs from ``configs/model/rawnet2.yaml``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import structlog
from numpy.typing import NDArray

from vaaniq.config.domains import RawNet2Config
from vaaniq.core.domain.entities import Embedding, Logits, Waveform
from vaaniq.core.errors import ModelNotReadyError
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.types import Label

log = structlog.get_logger(__name__)

Float32Array = NDArray[np.float32]


def _conv1d(x: Float32Array, kernel: Float32Array) -> Float32Array:
    """Valid 1-D convolution for ``[T]`` and kernel ``[K]`` → ``[T-K+1]``."""
    k = kernel.shape[0]
    if x.shape[0] < k:
        x = np.pad(x, (0, k - x.shape[0]))
    # correlate
    out = np.correlate(x, kernel, mode="valid").astype(np.float32)
    return out


class RawNet2Classifier(Classifier):
    """RawNet2-style approximate baseline (REQ-043)."""

    def __init__(
        self,
        config: RawNet2Config | None = None,
        *,
        rng: np.random.Generator | None = None,
        target_len: int = 16000,
    ) -> None:
        """Initialise convolutional filters.

        Args:
            config: RawNet2 training config.
            rng: RNG for init.
            target_len: Fixed sample length after crop/pad.
                # ASSUMPTION: OQ-014 - 1 s @ 16 kHz for CI speed.
        """
        self._config = config or RawNet2Config()
        self._rng = rng or np.random.default_rng(42)
        self._target_len = target_len
        self._k1 = self._rng.normal(0.0, 0.1, size=64).astype(np.float32)
        self._k2 = self._rng.normal(0.0, 0.1, size=32).astype(np.float32)
        self._w = self._rng.normal(0.0, 0.1, size=(8, 2)).astype(np.float32)
        self._b = np.zeros(2, dtype=np.float32)
        self._fitted = True

    def _prepare(self, samples: Float32Array) -> Float32Array:
        if samples.size >= self._target_len:
            return samples[: self._target_len]
        return np.pad(samples, (0, self._target_len - samples.size)).astype(np.float32)

    def _encode(self, samples: Float32Array) -> Float32Array:
        x = self._prepare(samples)
        h1 = np.tanh(_conv1d(x, self._k1))
        # max-pool
        pool = h1[::4]
        h2 = np.tanh(_conv1d(pool, self._k2))
        # global stats → 8-D
        feats = np.array(
            [
                float(np.mean(h2)),
                float(np.std(h2)),
                float(np.max(h2)),
                float(np.min(h2)),
                float(np.mean(np.abs(h2))),
                float(np.percentile(h2, 25)),
                float(np.percentile(h2, 75)),
                float(np.mean(np.square(h2))),
            ],
            dtype=np.float32,
        )
        return feats

    def predict(self, emb: Embedding) -> Logits:
        """Treat ``emb.vector`` as mono PCM samples (REQ-043 port adapter)."""
        if not self._fitted:
            raise ModelNotReadyError("RawNet2Classifier not ready")
        feats = self._encode(np.asarray(emb.vector, dtype=np.float32).reshape(-1))
        logits = feats @ self._w + self._b
        return Logits(values=logits.astype(np.float32), class_order=(Label.REAL, Label.FAKE))

    def predict_waveform(self, wav: Waveform) -> Logits:
        """Predict from a waveform."""
        return self.predict(
            Embedding(
                vector=np.asarray(wav.samples, dtype=np.float32),
                model_id="rawnet2",
                clip_id="adhoc",
            )
        )

    def train_epoch(
        self,
        waveforms: list[Waveform],
        labels: list[Label],
        *,
        learning_rate: float,
    ) -> float:
        """One SGD epoch on the linear head over frozen conv filters."""
        if not waveforms:
            return 0.0
        losses: list[float] = []
        for wav, lab in zip(waveforms, labels, strict=True):
            feats = self._encode(np.asarray(wav.samples, dtype=np.float32))
            logits = feats @ self._w + self._b
            # softmax CE
            shifted = logits - np.max(logits)
            ex = np.exp(shifted)
            probs = ex / np.sum(ex)
            y = 0 if lab == Label.REAL else 1
            losses.append(float(-np.log(max(float(probs[y]), 1e-8))))
            grad = probs.copy()
            grad[y] -= 1.0
            self._w -= (learning_rate * np.outer(feats, grad)).astype(np.float32)
            self._b -= (learning_rate * grad).astype(np.float32)
        return float(np.mean(losses))

    def save(self, path: Path) -> None:
        """Persist filters and head."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path, k1=self._k1, k2=self._k2, w=self._w, b=self._b, target_len=self._target_len
        )
        path.with_suffix(".json").write_text(
            json.dumps({"model": "rawnet2", "target_len": self._target_len}),
            encoding="utf-8",
        )
        log.info("rawnet2_saved", path=str(path))

    def load(self, path: Path) -> None:
        """Load filters and head."""
        data = np.load(Path(path))
        self._k1 = data["k1"].astype(np.float32)
        self._k2 = data["k2"].astype(np.float32)
        self._w = data["w"].astype(np.float32)
        self._b = data["b"].astype(np.float32)
        self._target_len = int(data["target_len"]) if "target_len" in data.files else 16000
        self._fitted = True
