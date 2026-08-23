"""Unit tests for embedding cache and frozen XLS-R extractor (ROADMAP-025-028)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vaaniq.core.domain.entities import Embedding, Waveform
from vaaniq.features.cache.filesystem import (
    FilesystemEmbeddingCache,
    embedding_cache_key,
    validate_embedding,
)
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor, write_feature_store_entry


def _wav(seconds: float = 0.5) -> Waveform:
    n = int(16000 * seconds)
    return Waveform(samples=np.zeros(n, dtype=np.float32), sample_rate_hz=16000)


def test_embedding_cache_roundtrip(tmp_path: Path) -> None:
    cache = FilesystemEmbeddingCache(tmp_path)
    key = embedding_cache_key(
        clip_id="c1",
        model_id="facebook/wav2vec2-xls-r-300m",
        preprocess_fingerprint="fp1",
    )
    emb = Embedding(
        vector=np.arange(8, dtype=np.float32),
        model_id="facebook/wav2vec2-xls-r-300m",
        clip_id="c1",
    )
    assert cache.get(key) is None
    cache.put(key, emb)
    hit = cache.get(key)
    assert hit is not None
    assert hit.clip_id == "c1"
    assert np.allclose(hit.vector, emb.vector)


def test_validate_embedding() -> None:
    emb = Embedding(vector=np.ones(4, dtype=np.float32), model_id="m", clip_id="c")
    validate_embedding(emb, expected_dim=4)


def test_frozen_xlsr_with_mock_backend(tmp_path: Path) -> None:
    cache = FilesystemEmbeddingCache(tmp_path)

    def backend(wav: Waveform) -> np.ndarray:
        return np.full(16, float(wav.samples.shape[0]), dtype=np.float32)

    extractor = FrozenXLSRExtractor(cache=cache, backend=backend)
    emb = extractor.extract(_wav(), clip_id="clip-a")
    assert emb.vector.shape == (16,)
    # resume / cache hit
    emb2 = extractor.extract(_wav(), clip_id="clip-a")
    assert np.allclose(emb.vector, emb2.vector)
    batch = extractor.extract_batch([(_wav(), "clip-a"), (_wav(), "clip-b")], resume=True)
    assert len(batch) == 2


def test_write_feature_store_entry(tmp_path: Path) -> None:
    path = tmp_path / "feat.npy"
    emb = Embedding(vector=np.ones(3, dtype=np.float32), model_id="m", clip_id="c")
    write_feature_store_entry(path, emb)
    assert path.is_file()
