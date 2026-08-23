"""Fixture-tree downloader for offline unit tests (ROADMAP-011)."""

from __future__ import annotations

import shutil
from pathlib import Path

from vaaniq.core.errors import DatasetError
from vaaniq.datasets.download.manager import DownloadManager
from vaaniq.observability.logging import get_logger

log = get_logger(__name__)


class MockDownloader(DownloadManager):
    """Materialise corpus trees from a checked-in fixture directory.

    Used by unit tests; never performs network I/O. Serves ROADMAP-011.
    """

    def __init__(self, fixture_root: Path) -> None:
        """Bind the fixture tree root.

        Args:
            fixture_root: Directory containing mock corpus trees / manifests.
        """
        self._fixture_root = fixture_root

    def ensure_local(self, source_id: str, dest: Path) -> Path:
        """Copy ``fixture_root/source_id`` (or the whole fixture root) to ``dest``.

        Args:
            source_id: Corpus identifier.
            dest: Destination directory.

        Returns:
            Path to the materialised tree.

        Raises:
            DatasetError: If neither a named subtree nor the fixture root exists.
        """
        named = self._fixture_root / source_id
        src = named if named.exists() else self._fixture_root
        if not src.exists():
            msg = f"mock fixture missing for source_id={source_id}"
            raise DatasetError(msg)
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / source_id
        if target.exists():
            log.info("mock_download_already_present", source_id=source_id, path=str(target))
            return target
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
        log.info("mock_download_complete", source_id=source_id, dest=str(target))
        return target
