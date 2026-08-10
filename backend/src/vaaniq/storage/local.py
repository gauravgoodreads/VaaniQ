"""Local filesystem object store stub (ROADMAP-009 / storage)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.object_store import ObjectStore


class LocalObjectStore(ObjectStore):
    """Filesystem-backed blob store under ``paths.object_store_root``.

    TODO(ROADMAP-009): implement put/get with safe key joining.
    """

    def __init__(self, root: Path) -> None:
        """Bind store root directory."""
        self._root = root

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Store object (deferred to ROADMAP-009)."""
        raise NotImplementedInPhaseError("ROADMAP-009", "LocalObjectStore.put")

    def get(self, key: str) -> bytes:
        """Fetch object (deferred to ROADMAP-009)."""
        raise NotImplementedInPhaseError("ROADMAP-009", "LocalObjectStore.get")

    def uri_for(self, key: str) -> str | Path:
        """Resolve URI (deferred to ROADMAP-009)."""
        raise NotImplementedInPhaseError("ROADMAP-009", "LocalObjectStore.uri_for")
