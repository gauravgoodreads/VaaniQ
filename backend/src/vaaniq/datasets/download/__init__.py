"""Offline-friendly download managers (ROADMAP-011)."""

from __future__ import annotations

from vaaniq.datasets.download.local_cache import LocalCacheDownloader
from vaaniq.datasets.download.manager import DownloadManager
from vaaniq.datasets.download.mock import MockDownloader

__all__ = [
    "DownloadManager",
    "LocalCacheDownloader",
    "MockDownloader",
]
