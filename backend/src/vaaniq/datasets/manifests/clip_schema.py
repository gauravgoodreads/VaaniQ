"""Clip metadata schema helpers stub (ROADMAP-012 / REQ-131-133)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import NotImplementedInPhaseError


def parse_clip_metadata(row: Mapping[str, Any]) -> ClipMetadata:
    """Validate and parse a raw metadata row into ``ClipMetadata``.

    TODO(ROADMAP-012): Pydantic validators for required fields and enums.
    """
    raise NotImplementedInPhaseError("ROADMAP-012", "parse_clip_metadata")
