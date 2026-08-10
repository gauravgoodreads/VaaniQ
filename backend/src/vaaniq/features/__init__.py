"""Features package public exports (Phase 1 stubs)."""

from __future__ import annotations

from vaaniq.features.cache.filesystem import FilesystemEmbeddingCache
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor

__all__ = [
    "FilesystemEmbeddingCache",
    "FrozenXLSRExtractor",
]
