"""Frozen XLS-R feature extractor (ROADMAP-025 / REQ-036, REQ-041).

Inference only — weights are frozen; no training path exists here.
ASSUMPTION: OQ-013 — mean-pool last transformer layer; window/hop from config.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any, cast

import numpy as np
import structlog

from vaaniq.config.domains import XlsrAasistConfig
from vaaniq.core.domain.entities import Embedding, Waveform
from vaaniq.core.errors import ModelNotReadyError
from vaaniq.core.ports.feature_extractor import FeatureExtractor
from vaaniq.features.cache.filesystem import (
    FilesystemEmbeddingCache,
    embedding_cache_key,
    validate_embedding,
)

log = structlog.get_logger(__name__)

EmbeddingBackend = Callable[[Waveform], np.ndarray]


class FrozenXLSRExtractor(FeatureExtractor):
    """Frozen wav2vec 2.0 XLS-R (300M) embedding extractor (REQ-041).

    Unit tests inject a mock ``backend``; production loads transformers lazily.
    """

    def __init__(
        self,
        config: XlsrAasistConfig | None = None,
        *,
        cache: FilesystemEmbeddingCache | None = None,
        preprocess_fingerprint: str = "default_preproc_v1",
        backend: EmbeddingBackend | None = None,
    ) -> None:
        """Bind config, optional cache, and optional inference backend.

        Args:
            config: XLS-R / AASIST model config.
            cache: Optional embedding cache for resume extraction.
            preprocess_fingerprint: Fingerprint included in cache keys.
            backend: Optional callable ``Waveform -> ndarray`` (tests/mocks).
        """
        self._config = config or XlsrAasistConfig()
        if not self._config.freeze_frontend:
            raise ModelNotReadyError("XLS-R frontend must remain frozen (REQ-041)")
        self._cache = cache
        self._preprocess_fingerprint = preprocess_fingerprint
        self._backend = backend
        self._model: Any | None = None  # optional torch module; requires [ml]
        self._processor: Any | None = None  # optional HF processor; requires [ml]

    def extract(self, wav: Waveform, *, clip_id: str) -> Embedding:
        """Extract (and optionally cache) an embedding for ``clip_id``.

        Args:
            wav: Preprocessed waveform.
            clip_id: Clip identifier.

        Returns:
            ``Embedding`` with float32 vector.
        """
        key = embedding_cache_key(
            clip_id=clip_id,
            model_id=self._config.xlsr_model_id,
            preprocess_fingerprint=self._preprocess_fingerprint,
        )
        if self._cache is not None:
            hit = self._cache.get(key)
            if hit is not None:
                log.info("embedding_cache_hit", clip_id=clip_id)
                return hit
        vector = self._infer(wav)
        emb = Embedding(vector=vector, model_id=self._config.xlsr_model_id, clip_id=clip_id)
        validate_embedding(emb)
        if self._cache is not None:
            self._cache.put(key, emb)
        log.info("embedding_extracted", clip_id=clip_id, dim=int(vector.shape[-1]))
        return emb

    def extract_batch(
        self,
        items: Sequence[tuple[Waveform, str]],
        *,
        resume: bool = True,
    ) -> list[Embedding]:
        """Batch extract with optional resume via cache (ROADMAP-025).

        Args:
            items: Sequence of ``(waveform, clip_id)``.
            resume: When True, skip clips already present in cache.

        Returns:
            Embeddings in the same order as ``items``.
        """
        out: list[Embedding] = []
        for wav, clip_id in items:
            if resume and self._cache is not None:
                key = embedding_cache_key(
                    clip_id=clip_id,
                    model_id=self._config.xlsr_model_id,
                    preprocess_fingerprint=self._preprocess_fingerprint,
                )
                hit = self._cache.get(key)
                if hit is not None:
                    out.append(hit)
                    continue
            out.append(self.extract(wav, clip_id=clip_id))
        return out

    def iter_extract(
        self,
        items: Iterator[tuple[Waveform, str]],
    ) -> Iterator[Embedding]:
        """Yield embeddings lazily for streaming extraction."""
        for wav, clip_id in items:
            yield self.extract(wav, clip_id=clip_id)

    def _infer(self, wav: Waveform) -> np.ndarray:
        if self._backend is not None:
            return np.asarray(self._backend(wav), dtype=np.float32)
        return self._infer_transformers(wav)

    def _infer_transformers(self, wav: Waveform) -> np.ndarray:
        """Lazy HF transformers inference (integration / GPU hosts)."""
        try:
            import torch
            from transformers import (
                AutoFeatureExtractor,
                Wav2Vec2Model,
            )
        except ImportError as exc:  # pragma: no cover
            raise ModelNotReadyError(
                "optional [ml] extras required for real XLS-R inference",
            ) from exc
        if self._model is None or self._processor is None:
            model_id = self._config.xlsr_model_id
            load_fe: Any = AutoFeatureExtractor.from_pretrained
            load_model: Any = Wav2Vec2Model.from_pretrained
            processor = load_fe(model_id)
            model = load_model(model_id)
            model.eval()
            for param in model.parameters():
                param.requires_grad_(False)
            self._processor = processor
            self._model = model
            log.info("xlsr_loaded_frozen", model_id=model_id)
        processor = cast("Any", self._processor)
        model = cast("Any", self._model)
        inputs = processor(
            wav.samples,
            sampling_rate=wav.sample_rate_hz,
            return_tensors="pt",
            padding=True,
        )
        with torch.inference_mode():
            hidden = model(**inputs).last_hidden_state
            pooled = hidden.mean(dim=1) if self._config.pooling == "mean" else hidden[:, -1, :]
        arr = pooled.squeeze(0).cpu().numpy()
        return np.asarray(arr, dtype=np.float32)


def write_feature_store_entry(path: Path, embedding: Embedding) -> None:
    """Persist a single embedding as ``.npz`` for offline feature stores.

    Args:
        path: Destination ``.npy`` path.
        embedding: Embedding to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, np.asarray(embedding.vector, dtype=np.float32))
