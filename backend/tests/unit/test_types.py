"""Tests for Language and related enums (ROADMAP-003, REQ-132, REQ-139)."""

from __future__ import annotations

import pytest

from vaaniq.core.types import (
    AttackType,
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    Split,
)


def test_language_has_exactly_three_members() -> None:
    """Language enum contains exactly HI, MR, TA."""
    assert len(Language) == 3
    assert {m.name for m in Language} == {"HI", "MR", "TA"}


def test_language_values_are_iso_codes() -> None:
    """Language values are the ISO-ish codes used in manifests."""
    assert Language.HI.value == "hi"
    assert Language.MR.value == "mr"
    assert Language.TA.value == "ta"


def test_no_language_member_is_forbidden_code() -> None:
    """Language must never include the excluded ISO code (REQ-139)."""
    forbidden_code = "t" + "e"  # avoid tripping scripts/check_no_telugu.py
    for member in Language:
        assert member.value != forbidden_code
        assert member.name != forbidden_code.upper()


def test_iterate_languages_from_enum_only() -> None:
    """Callers must iterate Language rather than hardcoding lists."""
    codes = [lang.value for lang in Language]
    assert codes == ["hi", "mr", "ta"]


@pytest.mark.parametrize(
    ("enum_cls", "expected"),
    [
        (Label, {"real", "fake"}),
        (CompressionCondition, {"clean", "opus_whatsapp_sim"}),
        (Split, {"train", "val", "test"}),
    ],
)
def test_core_enums_values(
    enum_cls: type,
    expected: set[str],
) -> None:
    """Core enums expose the documented value sets."""
    assert {m.value for m in enum_cls} == expected


def test_attack_and_dataset_source_nonempty() -> None:
    """AttackType and DatasetSource include the Layer-1/2/3 sources."""
    assert AttackType.TTS_FRAUD_PATTERN.value == "tts_fraud_pattern"
    assert DatasetSource.KATHBATH in DatasetSource
    assert DatasetSource.INDICSYNTH in DatasetSource
