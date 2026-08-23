"""Clean↔compressed pair helpers (ROADMAP-022 / OQ-028)."""

from __future__ import annotations

import hashlib
from dataclasses import replace

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import CompressionCondition


def make_pair_id(clean_clip_id: str) -> str:
    """Derive a stable pair id from the clean clip id.

    Args:
        clean_clip_id: Parent clean clip identifier.

    Returns:
        Hex digest pair id (REQ-035).
    """
    digest = hashlib.sha256(clean_clip_id.encode("utf-8")).hexdigest()
    return f"pair_{digest[:16]}"


def paired_clip_metadata(
    clean: ClipMetadata,
    *,
    compressed_clip_id: str,
    condition: CompressionCondition = CompressionCondition.OPUS_WHATSAPP_SIM,
) -> ClipMetadata:
    """Clone clean metadata for a compressed child sharing ``pair_id``.

    Args:
        clean: Clean parent metadata.
        compressed_clip_id: Child clip id.
        condition: Compression condition enum value.

    Returns:
        New ``ClipMetadata`` with shared ``pair_id``.
    """
    pair_id = clean.pair_id or make_pair_id(clean.clip_id)
    return replace(
        clean,
        clip_id=compressed_clip_id,
        compression_status=condition,
        pair_id=pair_id,
    )
