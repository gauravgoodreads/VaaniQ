"""Base row parser for source-specific manifests (ROADMAP-011 / ROADMAP-012)."""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import DatasetSource
from vaaniq.datasets.manifests.clip_schema import parse_clip_metadata
from vaaniq.datasets.normalizers.ids import normalize_clip_id, normalize_speaker_id


class BaseRowParser(ABC):
    """Normalise a source row then validate via ``parse_clip_metadata``.

    Serves ROADMAP-011 / ROADMAP-012 / REQ-131-133.
    """

    source: DatasetSource

    def parse(self, row: Mapping[str, object]) -> ClipMetadata:
        """Parse one raw row into ``ClipMetadata``.

        Args:
            row: Source-specific mapping (JSONL object or CSV row dict).

        Returns:
            Validated domain entity.
        """
        return parse_clip_metadata(self.normalize(dict(row)))

    def normalize(self, row: dict[str, object]) -> dict[str, object]:
        """Apply shared id cleanup and default ``source`` when missing.

        Args:
            row: Mutable copy of the raw row.

        Returns:
            Row ready for ``ClipMetadataModel`` validation.
        """
        if "source" not in row:
            row["source"] = self.source.value
        clip_raw = row.get("clip_id")
        if isinstance(clip_raw, str):
            row["clip_id"] = normalize_clip_id(clip_raw)
        speaker_raw = row.get("speaker_id")
        if speaker_raw is None:
            row["speaker_id"] = None
        elif isinstance(speaker_raw, str):
            row["speaker_id"] = normalize_speaker_id(speaker_raw)
        path_raw = row.pop("path", None)
        if path_raw is not None and row.get("uri") is None:
            row["uri"] = str(path_raw)
        return row
