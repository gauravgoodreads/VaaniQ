"""Whisper transcription — Groq cloud API or local faster-whisper."""

from __future__ import annotations

import io
import wave
from dataclasses import dataclass
from pathlib import Path

import httpx
import numpy as np
import structlog

from vaaniq.integrations.settings import IntegrationSettings, get_integration_settings

log = structlog.get_logger(__name__)

# Map Whisper language codes / names → VaaniQ languages where possible.
# Groq verbose_json reports full names ("hindi"); faster-whisper reports codes ("hi").
_WHISPER_TO_VAANIQ = {
    "hi": "hi",
    "mr": "mr",
    "ta": "ta",
    "en": "hi",  # fallback hint only — never Telugu
    "hindi": "hi",
    "marathi": "mr",
    "tamil": "ta",
}


def _map_language(lang: object) -> str | None:
    """Return the VaaniQ code for a Whisper language, else the raw value."""
    if not lang:
        return None
    raw = str(lang).strip()
    return _WHISPER_TO_VAANIQ.get(raw.lower(), raw)


@dataclass(slots=True)
class TranscriptResult:
    """Speech-to-text + language hint."""

    text: str
    language: str | None
    backend: str
    duration_sec: float | None = None


def _wav_bytes_from_mono(samples: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Encode float32 mono [-1,1] as 16-bit PCM WAV bytes."""
    pcm = np.clip(samples, -1.0, 1.0)
    ints = (pcm * 32767.0).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(ints.tobytes())
    return buf.getvalue()


def _transcribe_groq(
    wav_bytes: bytes,
    *,
    settings: IntegrationSettings,
    language_hint: str | None,
) -> TranscriptResult:
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    data: dict[str, str] = {
        "model": settings.groq_whisper_model,
        "response_format": "verbose_json",
        "temperature": "0",
    }
    if language_hint in {"hi", "mr", "ta", "en"}:
        data["language"] = language_hint
    files = {"file": ("clip.wav", wav_bytes, "audio/wav")}
    with httpx.Client(timeout=120.0) as client:
        res = client.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            data=data,
            files=files,
        )
        res.raise_for_status()
        payload = res.json()
    text = str(payload.get("text", "")).strip()
    return TranscriptResult(
        text=text,
        language=_map_language(payload.get("language")),
        backend="groq-whisper",
        duration_sec=float(payload["duration"]) if payload.get("duration") is not None else None,
    )


def _translate_groq(
    wav_bytes: bytes,
    *,
    settings: IntegrationSettings,
) -> TranscriptResult:
    """Speech-to-English via Groq Whisper translations (RQ / demo enrichment)."""
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    data: dict[str, str] = {
        "model": settings.groq_whisper_model,
        "response_format": "json",
        "temperature": "0",
    }
    files = {"file": ("clip.wav", wav_bytes, "audio/wav")}
    with httpx.Client(timeout=120.0) as client:
        res = client.post(
            "https://api.groq.com/openai/v1/audio/translations",
            headers=headers,
            data=data,
            files=files,
        )
        res.raise_for_status()
        payload = res.json()
    text = str(payload.get("text", "")).strip()
    return TranscriptResult(text=text, language="en", backend="groq-whisper-translate")


def _transcribe_local(
    samples: np.ndarray,
    sample_rate: int,
    *,
    settings: IntegrationSettings,
    language_hint: str | None,
) -> TranscriptResult:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Run: uv pip install faster-whisper"
        ) from exc

    import os

    device = os.environ.get("VAANIQ_WHISPER_DEVICE", "").strip().lower()
    if not device:
        try:
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"
    compute = "float16" if device == "cuda" else "int8"
    model = WhisperModel(settings.local_whisper_model, device=device, compute_type=compute)
    lang = language_hint if language_hint in {"hi", "mr", "ta", "en"} else None
    segments, info = model.transcribe(
        samples.astype(np.float32),
        language=lang,
        beam_size=1,
        vad_filter=True,
    )
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return TranscriptResult(
        text=text,
        language=_map_language(getattr(info, "language", None)),
        backend=f"local-whisper:{settings.local_whisper_model}@{device}",
        duration_sec=float(len(samples) / max(sample_rate, 1)),
    )


def transcribe_waveform(
    samples: np.ndarray,
    sample_rate: int = 16000,
    *,
    language_hint: str | None = None,
    settings: IntegrationSettings | None = None,
) -> TranscriptResult | None:
    """Transcribe mono float audio via Groq Whisper or local faster-whisper.

    Returns ``None`` when backends are disabled / unavailable (demo still works).
    """
    cfg = settings or get_integration_settings()
    backend = cfg.whisper_backend
    flat = np.asarray(samples, dtype=np.float32).reshape(-1)
    if flat.size < sample_rate // 4:
        return TranscriptResult(text="", language=language_hint, backend="skipped-short")

    prefer_groq = backend in {"auto", "groq"} and cfg.groq_enabled
    prefer_local = backend in {"auto", "local"}

    if prefer_groq:
        try:
            wav_bytes = _wav_bytes_from_mono(flat, sample_rate)
            result = _transcribe_groq(wav_bytes, settings=cfg, language_hint=language_hint)
            log.info("whisper_ok", backend=result.backend, n_chars=len(result.text))
            return result
        except Exception as exc:
            log.warning("groq_whisper_failed", error=str(exc))
            if backend == "groq":
                return TranscriptResult(text="", language=language_hint, backend="groq-error")

    if prefer_local and backend != "off":
        try:
            result = _transcribe_local(flat, sample_rate, settings=cfg, language_hint=language_hint)
            log.info("whisper_ok", backend=result.backend, n_chars=len(result.text))
            return result
        except Exception as exc:
            log.warning("local_whisper_failed", error=str(exc))

    return TranscriptResult(text="", language=language_hint, backend="unavailable")


def translate_waveform(
    samples: np.ndarray,
    sample_rate: int = 16000,
    *,
    settings: IntegrationSettings | None = None,
) -> TranscriptResult | None:
    """Translate speech to English via Groq Whisper translations.

    Returns ``None`` when Groq is disabled. Does not invent a translation.
    """
    cfg = settings or get_integration_settings()
    if not cfg.groq_enabled or cfg.whisper_backend == "off":
        return None
    flat = np.asarray(samples, dtype=np.float32).reshape(-1)
    if flat.size < sample_rate // 4:
        return TranscriptResult(text="", language="en", backend="skipped-short")
    try:
        wav_bytes = _wav_bytes_from_mono(flat, sample_rate)
        result = _translate_groq(wav_bytes, settings=cfg)
        log.info("whisper_translate_ok", backend=result.backend, n_chars=len(result.text))
        return result
    except Exception as exc:
        log.warning("groq_whisper_translate_failed", error=str(exc))
        return TranscriptResult(text="", language="en", backend="groq-translate-error")


def transcribe_file(
    path: Path,
    *,
    language_hint: str | None = None,
) -> TranscriptResult | None:
    """Load a WAV/FLAC path and transcribe."""
    import soundfile as sf

    data, sr = sf.read(str(path), always_2d=False, dtype="float32")
    if getattr(data, "ndim", 1) > 1:
        data = np.mean(data, axis=1)
    return transcribe_waveform(
        np.asarray(data, dtype=np.float32),
        int(sr),
        language_hint=language_hint,
    )
