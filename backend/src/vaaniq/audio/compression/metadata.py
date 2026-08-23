"""Compression run metadata (ROADMAP-021-023 / REQ-113)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompressionMetadata:
    """Metadata for a compressed twin of a clean clip.

    Serves REQ-035, REQ-113. ASSUMPTION: OQ-007 for codec defaults.
    """

    pair_id: str
    parent_clip_id: str
    child_clip_id: str
    codec: str
    bitrate_kbps: int
    quality: str
    sample_rate_hz: int
    channels: int
    container: str
    compression_ratio: float
    signal_loss_db: float
