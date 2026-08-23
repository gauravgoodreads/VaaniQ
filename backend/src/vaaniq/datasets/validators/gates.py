"""Dataset clip validators and licence gating (ROADMAP-012 / REQ-130)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import DatasetError
from vaaniq.core.types import Language


def language_filter(
    clips: Sequence[ClipMetadata],
    languages: Sequence[Language],
) -> list[ClipMetadata]:
    """Keep clips whose language is in ``languages``.

    Args:
        clips: Input clip metadata.
        languages: Allowed languages (typically ``list(Language)`` or a subset).

    Returns:
        Filtered clip list preserving order.

    Serves:
        ROADMAP-012 / REQ-132 / REQ-139.
    """
    allowed = set(languages)
    return [clip for clip in clips if clip.language in allowed]


def require_fields(clip: ClipMetadata) -> None:
    """Raise if required ClipMetadata fields are missing or invalid.

    Args:
        clip: Clip to validate.

    Raises:
        DatasetError: On empty ids, non-positive rate/duration, or empty provenance.

    Serves:
        ROADMAP-012 / REQ-131-133.
    """
    if not clip.clip_id.strip():
        raise DatasetError("clip_id is required")
    if clip.sample_rate_hz <= 0:
        raise DatasetError("sample_rate_hz must be positive")
    if clip.duration_sec <= 0:
        raise DatasetError("duration_sec must be positive")
    if not clip.dataset_source.strip():
        raise DatasetError("dataset_source is required")


def licence_gate(*, gated: bool, token_present: bool) -> None:
    """Fail fast when a gated corpus is accessed without credentials.

    Args:
        gated: Whether the source requires gated access (REQ-130).
        token_present: Whether an auth token (e.g. ``HF_TOKEN``) is available.

    Raises:
        DatasetError: If ``gated`` is True and ``token_present`` is False.

    Serves:
        ROADMAP-011 / REQ-130.
    """
    if gated and not token_present:
        raise DatasetError("gated dataset requires an auth token (REQ-130)")
