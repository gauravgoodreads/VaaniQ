"""Unit tests for Whisper transcription routing (no network)."""

from __future__ import annotations

import io
import wave

import numpy as np
import pytest

from vaaniq.integrations import whisper_client
from vaaniq.integrations.settings import IntegrationSettings
from vaaniq.integrations.whisper_client import (
    TranscriptResult,
    _map_language,
    _wav_bytes_from_mono,
    transcribe_waveform,
    translate_waveform,
)


def _settings(*, key: str = "", backend: str = "auto") -> IntegrationSettings:
    return IntegrationSettings(
        groq_api_key=key,
        hf_token="",
        whisper_backend=backend,
        groq_whisper_model="whisper-large-v3",
        groq_llm_model="openai/gpt-oss-20b",
        local_whisper_model="base",
        enable_llm_enrichment=False,
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("hi", "hi"),
        ("Hindi", "hi"),
        ("marathi", "mr"),
        ("TAMIL", "ta"),
        ("en", "hi"),
        ("bengali", "bengali"),
        (None, None),
        ("", None),
    ],
)
def test_map_language_accepts_codes_and_names(raw: object, expected: str | None) -> None:
    assert _map_language(raw) == expected


def test_wav_bytes_round_trip() -> None:
    samples = np.linspace(-1.0, 1.0, 1600, dtype=np.float32)
    data = _wav_bytes_from_mono(samples, 16000)
    with wave.open(io.BytesIO(data), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000
        assert wf.getnframes() == 1600


def test_short_clip_skips_transcription() -> None:
    result = transcribe_waveform(np.zeros(100, dtype=np.float32), 16000, settings=_settings())
    assert result is not None
    assert result.backend == "skipped-short"


def test_groq_used_when_key_present(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_groq(_wav: bytes, **_kw: object) -> TranscriptResult:
        return TranscriptResult(text="नमस्ते", language="hi", backend="groq-whisper")

    monkeypatch.setattr(whisper_client, "_transcribe_groq", fake_groq)
    result = transcribe_waveform(
        np.zeros(16000, dtype=np.float32), 16000, settings=_settings(key="test-key")
    )
    assert result is not None
    assert result.backend == "groq-whisper"
    assert result.language == "hi"


def test_groq_failure_falls_back_to_local(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_groq(_wav: bytes, **_kw: object) -> TranscriptResult:
        raise RuntimeError("429 rate limited")

    def fake_local(_samples: np.ndarray, _sr: int, **_kw: object) -> TranscriptResult:
        return TranscriptResult(text="ok", language="mr", backend="local-whisper:base@cpu")

    monkeypatch.setattr(whisper_client, "_transcribe_groq", broken_groq)
    monkeypatch.setattr(whisper_client, "_transcribe_local", fake_local)
    result = transcribe_waveform(
        np.zeros(16000, dtype=np.float32), 16000, settings=_settings(key="test-key")
    )
    assert result is not None
    assert result.backend.startswith("local-whisper")


def test_groq_only_backend_reports_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_groq(_wav: bytes, **_kw: object) -> TranscriptResult:
        raise RuntimeError("401")

    monkeypatch.setattr(whisper_client, "_transcribe_groq", broken_groq)
    result = transcribe_waveform(
        np.zeros(16000, dtype=np.float32),
        16000,
        language_hint="ta",
        settings=_settings(key="test-key", backend="groq"),
    )
    assert result is not None
    assert result.backend == "groq-error"
    assert result.language == "ta"


def test_off_backend_is_unavailable() -> None:
    result = transcribe_waveform(
        np.zeros(16000, dtype=np.float32), 16000, settings=_settings(backend="off")
    )
    assert result is not None
    assert result.backend == "unavailable"


def test_translate_requires_groq_key() -> None:
    assert translate_waveform(np.zeros(16000, dtype=np.float32), settings=_settings()) is None


def test_translate_uses_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_translate(_wav: bytes, **_kw: object) -> TranscriptResult:
        return TranscriptResult(text="hello", language="en", backend="groq-whisper-translate")

    monkeypatch.setattr(whisper_client, "_translate_groq", fake_translate)
    result = translate_waveform(
        np.zeros(16000, dtype=np.float32), settings=_settings(key="test-key")
    )
    assert result is not None
    assert result.text == "hello"
