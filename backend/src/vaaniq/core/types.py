"""Core enumerations for VaaniQ.

Languages are exactly Hindi, Marathi, and Tamil (REQ-002-004, REQ-132, REQ-139).
Telugu is not a project language. ROADMAP-003.
"""

from __future__ import annotations

from enum import StrEnum


class Language(StrEnum):
    """Supported project languages (REQ-132, REQ-139).

    Iterate ``Language`` wherever a language list is needed - never hardcode.
    """

    HI = "hi"
    MR = "mr"
    TA = "ta"


class Label(StrEnum):
    """Binary deepfake label (REQ-133)."""

    REAL = "real"
    FAKE = "fake"


class CompressionCondition(StrEnum):
    """Compression condition for a clip (REQ-005, REQ-035).

    ``OPUS_WHATSAPP_SIM`` is the WhatsApp-style Opus simulation (OQ-007).
    """

    CLEAN = "clean"
    OPUS_WHATSAPP_SIM = "opus_whatsapp_sim"


class AttackType(StrEnum):
    """Generation / attack family for fake audio (REQ-081, REQ-133)."""

    TTS = "tts"
    VOICE_CLONE = "voice_clone"
    TTS_FRAUD_PATTERN = "tts_fraud_pattern"
    VOICE_CLONE_FRAUD_PATTERN = "voice_clone_fraud_pattern"


class DatasetSource(StrEnum):
    """Provenance of a clip (REQ-101-106, REQ-133)."""

    KATHBATH = "kathbath"
    INDICVOICES_R = "indicvoices_r"
    COMMON_VOICE = "common_voice"
    INDICSYNTH = "indicsynth"
    TEAM_RECORDING = "team_recording"
    PARLER_TTS = "parler_tts"
    XTTS_V2 = "xtts_v2"


class Split(StrEnum):
    """Dataset split membership (REQ-099)."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class ReliabilityLevel(StrEnum):
    """UI reliability badge states (REQ-062, OQ-010)."""

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class ExportFormat(StrEnum):
    """Human-study export formats (REQ-069)."""

    CSV = "csv"
    JSON = "json"
