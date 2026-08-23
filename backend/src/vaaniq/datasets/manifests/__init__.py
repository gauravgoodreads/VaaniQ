"""Clip manifest schema exports (ROADMAP-012)."""

from __future__ import annotations

from vaaniq.datasets.manifests.clip_schema import ClipMetadataModel, parse_clip_metadata

__all__ = [
    "ClipMetadataModel",
    "parse_clip_metadata",
]
