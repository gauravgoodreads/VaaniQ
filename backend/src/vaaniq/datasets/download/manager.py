"""Download manager port (ROADMAP-011 / REQ-130)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class DownloadManager(ABC):
    """Ensure a corpus tree is available on local disk.

    Default implementations used by unit tests never touch the network.
    Serves ROADMAP-011 / REQ-130.
    """

    @abstractmethod
    def ensure_local(self, source_id: str, dest: Path) -> Path:
        """Materialise ``source_id`` under ``dest`` and return the local root.

        Args:
            source_id: Corpus identifier (typically a ``DatasetSource`` value).
            dest: Destination directory for the local tree.

        Returns:
            Path to the local corpus root ready for offline loaders.
        """
