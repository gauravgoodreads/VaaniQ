"""Filesystem embedding cache stub (ROADMAP-026 / REQ-037)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Embedding
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.embedding_cache import EmbeddingCache


class FilesystemEmbeddingCache(EmbeddingCache):
    """Disk-backed embedding cache keyed by clip id + config hash.

    TODO(ROADMAP-026): atomic writes under ``paths.embedding_cache_root``.
    """

    def get(self, key: str) -> Embedding | None:
        """Fetch cached embedding (deferred to ROADMAP-026)."""
        raise NotImplementedInPhaseError("ROADMAP-026", "FilesystemEmbeddingCache.get")

    def put(self, key: str, embedding: Embedding) -> None:
        """Store embedding (deferred to ROADMAP-026)."""
        raise NotImplementedInPhaseError("ROADMAP-026", "FilesystemEmbeddingCache.put")
