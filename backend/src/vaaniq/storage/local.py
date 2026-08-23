"""Local filesystem object store (ROADMAP-009 / storage)."""

from __future__ import annotations

from pathlib import Path

import structlog

from vaaniq.core.errors import PersistenceError, ValidationError
from vaaniq.core.ports.object_store import ObjectStore

log = structlog.get_logger(__name__)


class LocalObjectStore(ObjectStore):
    """Filesystem-backed blob store under ``paths.object_store_root``."""

    def __init__(self, root: Path) -> None:
        """Bind store root directory."""
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Store object bytes under a safe relative key.

        Args:
            key: Relative object key (no ``..``).
            data: Raw bytes.
            content_type: Optional MIME (stored only in logs for now).

        Returns:
            Filesystem URI string.
        """
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        log.info(
            "object_stored",
            key=key,
            bytes=len(data),
            content_type=content_type,
        )
        return str(path.resolve())

    def get(self, key: str) -> bytes:
        """Fetch object bytes.

        Args:
            key: Relative object key.

        Returns:
            Stored bytes.

        Raises:
            PersistenceError: If the key is missing.
        """
        path = self._resolve(key)
        if not path.is_file():
            raise PersistenceError(f"object not found: {key}")
        return path.read_bytes()

    def uri_for(self, key: str) -> str | Path:
        """Resolve absolute path for ``key`` without requiring existence."""
        return self._resolve(key)

    def _resolve(self, key: str) -> Path:
        if not key or key.startswith("/") or ".." in Path(key).parts:
            raise ValidationError(f"unsafe object store key: {key}")
        path = (self._root / key).resolve()
        root = self._root.resolve()
        if root not in path.parents and path != root:
            raise ValidationError(f"object store key escapes root: {key}")
        return path
