"""Object storage port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class ObjectStore(ABC):
    """Blob storage for audio and artefacts.

    Implementations: LocalObjectStore, S3ObjectStore (ROADMAP-009 / storage).
    """

    @abstractmethod
    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Store ``data`` under ``key`` and return a resolvable URI.

        Args:
            key: Object key.
            data: Raw bytes.
            content_type: Optional MIME type.
        """

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Fetch object bytes by ``key``.

        Raises:
            PersistenceError: If the key is missing.
        """

    @abstractmethod
    def uri_for(self, key: str) -> str | Path:
        """Return a URI or path for ``key`` without loading bytes."""
