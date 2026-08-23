"""Identifier normalisers for clip and speaker ids (ROADMAP-012)."""

from __future__ import annotations


def normalize_clip_id(raw: str) -> str:
    """Strip surrounding whitespace from a clip identifier.

    Args:
        raw: Raw clip id from a manifest or CSV row.

    Returns:
        Normalised clip id.

    Serves:
        ROADMAP-012 / REQ-131.
    """
    return raw.strip()


def normalize_speaker_id(raw: str | None) -> str | None:
    """Normalise a speaker id; empty strings become ``None``.

    Args:
        raw: Raw speaker id, possibly null.

    Returns:
        Stripped speaker id, or ``None`` when absent/blank.

    Serves:
        ROADMAP-012 / REQ-131.
    """
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None
