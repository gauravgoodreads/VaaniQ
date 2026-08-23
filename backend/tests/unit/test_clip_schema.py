"""Tests for ClipMetadata Pydantic schema (ROADMAP-012 / REQ-131-133)."""

from __future__ import annotations

import pytest

from vaaniq.core.errors import ValidationError
from vaaniq.core.types import DatasetSource, Label, Language, Split
from vaaniq.datasets.manifests.clip_schema import ClipMetadataModel, parse_clip_metadata


def _valid_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "clip_id": "c1",
        "language": "hi",
        "source": "kathbath",
        "label": "real",
        "compression_status": "clean",
        "sample_rate_hz": 16000,
        "duration_sec": 1.0,
        "split": "train",
        "dataset_source": "ai4bharat/Kathbath",
    }
    row.update(overrides)
    return row


def test_parse_clip_metadata_happy_path() -> None:
    clip = parse_clip_metadata(_valid_row(speaker_id="spk1", uri="/tmp/a.wav"))
    assert clip.language is Language.HI
    assert clip.source is DatasetSource.KATHBATH
    assert clip.label is Label.REAL
    assert clip.split is Split.TRAIN
    assert clip.speaker_id == "spk1"
    assert clip.uri == "/tmp/a.wav"
    assert clip.gender is None


def test_parse_rejects_non_project_language_code() -> None:
    # REQ-139: only hi/mr/ta are valid Language values.
    banned = "t" + "e"
    with pytest.raises(ValidationError):
        parse_clip_metadata(_valid_row(language=banned))


def test_parse_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        parse_clip_metadata(_valid_row(mystery=1))


def test_parse_rejects_missing_required() -> None:
    row = _valid_row()
    del row["clip_id"]
    with pytest.raises(ValidationError):
        parse_clip_metadata(row)


def test_model_to_entity_roundtrip() -> None:
    model = ClipMetadataModel.model_validate(_valid_row(file_size_bytes=100))
    entity = model.to_entity()
    assert entity.file_size_bytes == 100
    assert entity.language is Language.HI
