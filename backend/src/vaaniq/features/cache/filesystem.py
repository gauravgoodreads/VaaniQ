"""Filesystem embedding cache (ROADMAP-026 / REQ-037, ROADMAP-028)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import structlog

from vaaniq.core.domain.entities import Embedding
from vaaniq.core.errors import PersistenceError, ValidationError
from vaaniq.core.ports.embedding_cache import EmbeddingCache

log = structlog.get_logger(__name__)


def embedding_cache_key(
    *,
    clip_id: str,
    model_id: str,
    preprocess_fingerprint: str,
) -> str:
    """Build a stable cache key (ROADMAP-026).

    Args:
        clip_id: Clip identifier.
        model_id: Frontend model id (e.g. XLS-R HF id).
        preprocess_fingerprint: Hash of preprocess config.

    Returns:
        Filesystem-safe key string.
    """
    raw = f"{clip_id}|{model_id}|{preprocess_fingerprint}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{digest[:2]}/{digest}"


class FilesystemEmbeddingCache(EmbeddingCache):
    """Disk-backed embedding cache with checksum verification (REQ-037)."""

    def __init__(self, root: Path | None = None) -> None:
        """Bind cache root.

        Args:
            root: Directory for ``.npz`` + ``.meta.json`` pairs.
        """
        self._root = root or Path("./data/embedding_cache")
        self._root.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Embedding | None:
        """Fetch cached embedding if present and checksum matches.

        Args:
            key: Cache key from ``embedding_cache_key``.

        Returns:
            Embedding or ``None`` on miss/corruption.
        """
        npy_path, meta_path = self._paths(key)
        if not npy_path.is_file() or not meta_path.is_file():
            return None
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        vector = np.load(npy_path)
        checksum = self._checksum(vector)
        if checksum != meta.get("checksum_sha256"):
            log.warning("embedding_cache_checksum_mismatch", key=key)
            return None
        return Embedding(
            vector=np.asarray(vector, dtype=np.float32),
            model_id=str(meta["model_id"]),
            clip_id=str(meta["clip_id"]),
        )

    def put(self, key: str, embedding: Embedding) -> None:
        """Atomically store embedding vector and metadata (ROADMAP-028).

        Args:
            key: Cache key.
            embedding: Embedding to persist.
        """
        npy_path, meta_path = self._paths(key)
        npy_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_npy = npy_path.with_suffix(".tmp.npy")
        tmp_meta = meta_path.with_suffix(".tmp.json")
        np.save(tmp_npy, np.asarray(embedding.vector, dtype=np.float32))
        meta = {
            "clip_id": embedding.clip_id,
            "model_id": embedding.model_id,
            "checksum_sha256": self._checksum(embedding.vector),
            "shape": list(embedding.vector.shape),
        }
        tmp_meta.write_text(json.dumps(meta, sort_keys=True), encoding="utf-8")
        tmp_npy.replace(npy_path)
        tmp_meta.replace(meta_path)
        log.info("embedding_cached", key=key, clip_id=embedding.clip_id)

    def _paths(self, key: str) -> tuple[Path, Path]:
        if not key or ".." in Path(key).parts:
            raise ValidationError(f"unsafe embedding cache key: {key}")
        base = (self._root / key).resolve()
        root = self._root.resolve()
        if root not in base.parents and base != root:
            raise ValidationError(f"embedding cache key escapes root: {key}")
        return Path(str(base) + ".npy"), Path(str(base) + ".meta.json")

    @staticmethod
    def _checksum(vector: np.ndarray) -> str:
        arr = np.asarray(vector, dtype=np.float32)
        return hashlib.sha256(arr.tobytes()).hexdigest()


def validate_embedding(embedding: Embedding, *, expected_dim: int | None = None) -> None:
    """Validate embedding finiteness and optional dimensionality (ROADMAP-028).

    Args:
        embedding: Candidate embedding.
        expected_dim: Optional last-dimension size.

    Raises:
        PersistenceError: If invalid.
    """
    if embedding.vector.size == 0:
        raise PersistenceError("empty embedding")
    if not np.isfinite(embedding.vector).all():
        raise PersistenceError("embedding contains non-finite values")
    if expected_dim is not None and int(embedding.vector.shape[-1]) != expected_dim:
        raise PersistenceError("embedding dimension mismatch")
