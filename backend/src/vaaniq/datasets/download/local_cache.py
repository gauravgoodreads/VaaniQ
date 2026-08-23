"""Copy/link corpus material from a local cache root (ROADMAP-011)."""

from __future__ import annotations

import shutil
from pathlib import Path

from vaaniq.core.errors import DatasetError
from vaaniq.datasets.download.manager import DownloadManager
from vaaniq.observability.logging import get_logger

log = get_logger(__name__)


class LocalCacheDownloader(DownloadManager):
    """Populate ``dest`` by copying or linking from ``cache_root``.

    Never opens a network connection. Serves ROADMAP-011 / REQ-130.
    """

    def __init__(self, cache_root: Path, *, use_symlinks: bool = False) -> None:
        """Bind the on-disk cache root.

        Args:
            cache_root: Directory containing ``{source_id}/`` subtrees.
            use_symlinks: When True, symlink the source tree; else copy.
        """
        self._cache_root = cache_root
        self._use_symlinks = use_symlinks

    def ensure_local(self, source_id: str, dest: Path) -> Path:
        """Copy or link ``cache_root/source_id`` into ``dest``.

        Args:
            source_id: Corpus identifier.
            dest: Destination directory.

        Returns:
            ``dest`` after materialisation.

        Raises:
            DatasetError: If the cached source tree is missing.
        """
        src = self._cache_root / source_id
        if not src.exists():
            msg = f"cache miss for source_id={source_id} under {self._cache_root}"
            raise DatasetError(msg)
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / source_id
        if target.exists():
            log.info("local_cache_already_present", source_id=source_id, path=str(target))
            return target
        if self._use_symlinks:
            target.symlink_to(src.resolve(), target_is_directory=src.is_dir())
        elif src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
        log.info("local_cache_materialised", source_id=source_id, dest=str(target))
        return target
