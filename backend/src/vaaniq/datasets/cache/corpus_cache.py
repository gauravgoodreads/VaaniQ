"""On-disk corpus cache keyed by source id and checksum (ROADMAP-011)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.observability.logging import get_logger

log = get_logger(__name__)


class CorpusCache:
    """Map ``(source_id, checksum)`` pairs to paths under a configurable root.

    Serves ROADMAP-011 / REQ-137 (checksum-aware local materialisation).
    """

    def __init__(self, root: Path) -> None:
        """Bind the cache root directory.

        Args:
            root: Parent directory for cache entries.
        """
        self._root = root

    @property
    def root(self) -> Path:
        """Return the cache root path."""
        return self._root

    def path_for(self, source_id: str, checksum: str) -> Path:
        """Return the canonical path for a ``(source_id, checksum)`` key.

        Args:
            source_id: Corpus identifier.
            checksum: Content checksum (e.g. SHA-256 hex).

        Returns:
            Path under ``root / source_id / checksum``.
        """
        return self._root / source_id / checksum

    def get(self, source_id: str, checksum: str) -> Path | None:
        """Return the cache path if it already exists.

        Args:
            source_id: Corpus identifier.
            checksum: Content checksum.

        Returns:
            Existing path, or ``None`` on a miss.
        """
        path = self.path_for(source_id, checksum)
        if path.exists():
            log.info("corpus_cache_hit", source_id=source_id, checksum=checksum)
            return path
        log.info("corpus_cache_miss", source_id=source_id, checksum=checksum)
        return None

    def ensure_dir(self, source_id: str, checksum: str) -> Path:
        """Create and return the cache directory for a key.

        Args:
            source_id: Corpus identifier.
            checksum: Content checksum.

        Returns:
            Created (or existing) directory path.
        """
        path = self.path_for(source_id, checksum)
        path.mkdir(parents=True, exist_ok=True)
        return path
