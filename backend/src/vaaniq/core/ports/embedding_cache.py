"""Embedding cache port (REQ-037)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vaaniq.core.domain.entities import Embedding


class EmbeddingCache(ABC):
    """Persist and retrieve XLS-R embeddings.

    Serves REQ-037. Implementation: FilesystemEmbeddingCache (ROADMAP-026).
    """

    @abstractmethod
    def get(self, key: str) -> Embedding | None:
        """Return a cached embedding or ``None`` on miss.

        Args:
            key: Cache key (clip id + config hash).
        """

    @abstractmethod
    def put(self, key: str, embedding: Embedding) -> None:
        """Store ``embedding`` under ``key``.

        Args:
            key: Cache key.
            embedding: Value to persist.
        """
