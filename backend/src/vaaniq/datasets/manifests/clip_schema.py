"""Clip metadata Pydantic schema and parser (ROADMAP-012 / REQ-131-133)."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import ValidationError
from vaaniq.core.types import (
    AttackType,
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    Split,
)


class ClipMetadataModel(BaseModel):
    """I/O boundary model for clip manifests (REQ-131-133 / ROADMAP-012).

    ``extra='forbid'`` rejects unknown keys at parse time.
    Optional enrichment fields: ``# ASSUMPTION: OQ-036``.
    """

    model_config = ConfigDict(extra="forbid")

    clip_id: str
    language: Language
    source: DatasetSource
    label: Label
    compression_status: CompressionCondition
    sample_rate_hz: int
    duration_sec: float
    split: Split
    dataset_source: str
    speaker_id: str | None = None
    attack_type: AttackType | None = None
    generation_model: str | None = None
    pair_id: str | None = None
    consent_ref: str | None = None
    # ASSUMPTION: OQ-036
    gender: str | None = None
    file_size_bytes: int | None = None
    speaker_age: int | None = None
    emotion: str | None = None
    recording_medium: str | None = None
    quality: str | None = None
    checksum_sha256: str | None = None
    uri: str | None = None

    def to_entity(self) -> ClipMetadata:
        """Convert to the domain ``ClipMetadata`` dataclass.

        Returns:
            Immutable domain entity (REQ-131-133).
        """
        return ClipMetadata(
            clip_id=self.clip_id,
            language=self.language,
            source=self.source,
            label=self.label,
            compression_status=self.compression_status,
            sample_rate_hz=self.sample_rate_hz,
            duration_sec=self.duration_sec,
            split=self.split,
            dataset_source=self.dataset_source,
            speaker_id=self.speaker_id,
            attack_type=self.attack_type,
            generation_model=self.generation_model,
            pair_id=self.pair_id,
            consent_ref=self.consent_ref,
            gender=self.gender,
            file_size_bytes=self.file_size_bytes,
            speaker_age=self.speaker_age,
            emotion=self.emotion,
            recording_medium=self.recording_medium,
            quality=self.quality,
            checksum_sha256=self.checksum_sha256,
            uri=self.uri,
        )


def parse_clip_metadata(row: Mapping[str, object]) -> ClipMetadata:
    """Validate and parse a raw metadata row into ``ClipMetadata``.

    Args:
        row: Mapping of field names to values (JSONL/CSV cell values).

    Returns:
        Validated domain ``ClipMetadata``.

    Raises:
        ValidationError: If required fields are missing or enums are invalid.

    Serves:
        ROADMAP-012 / REQ-131-133.
    """
    try:
        model = ClipMetadataModel.model_validate(dict(row))
    except PydanticValidationError as exc:
        msg = f"invalid clip metadata: {exc}"
        raise ValidationError(msg) from exc
    return model.to_entity()
