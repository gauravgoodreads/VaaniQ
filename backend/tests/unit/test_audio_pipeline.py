"""Unit tests for audio transforms and loaders (ROADMAP-019-024)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from hypothesis import given
from hypothesis import strategies as st

from vaaniq.audio.compression.pairing import make_pair_id, paired_clip_metadata
from vaaniq.audio.io.soundfile_loader import SoundFileLoader
from vaaniq.audio.transforms.augment import additive_noise_augment, gain_augment
from vaaniq.audio.transforms.ops import (
    peak_normalize,
    resample_linear,
    to_mono,
    trim_duration,
    trim_silence,
)
from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.audio.transforms.spectrogram import mel_spectrogram, stft_magnitude
from vaaniq.audio.transforms.validator import MagicByteValidator
from vaaniq.config.domains import AudioPreprocessingConfig
from vaaniq.core.domain.entities import ClipMetadata, UploadBlob, Waveform
from vaaniq.core.errors import ValidationError
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    Split,
)


def _sine(sr: int = 16000, seconds: float = 1.0, freq: float = 440.0) -> Waveform:
    n = int(sr * seconds)
    t = np.arange(n, dtype=np.float32) / np.float32(sr)
    samples = (0.2 * np.sin(2.0 * np.pi * freq * t)).astype(np.float32)
    return Waveform(samples=samples, sample_rate_hz=sr)


def test_to_mono_mean() -> None:
    stereo = np.stack([np.ones(8, dtype=np.float32), np.zeros(8, dtype=np.float32)], axis=1)
    mono = to_mono(stereo)
    assert mono.shape == (8,)
    assert np.allclose(mono, 0.5)


@given(
    n=st.integers(min_value=8, max_value=4000),
    src=st.sampled_from([8000, 16000, 22050]),
    dst=st.sampled_from([8000, 16000]),
)
def test_resample_preserves_finiteness(n: int, src: int, dst: int) -> None:
    samples = np.linspace(-0.5, 0.5, n, dtype=np.float32)
    out = resample_linear(samples, src_hz=src, dst_hz=dst)
    assert out.dtype == np.float32
    assert np.isfinite(out).all()
    assert out.ndim == 1


@given(n=st.integers(min_value=1, max_value=2000))
def test_peak_normalize_bound(n: int) -> None:
    rng = np.random.default_rng(0)
    samples = rng.normal(0, 1, size=n).astype(np.float32)
    out = peak_normalize(samples, target_peak=0.95)
    if float(np.max(np.abs(samples))) > 0:
        assert float(np.max(np.abs(out))) == pytest.approx(0.95, rel=1e-5, abs=1e-5)


def test_trim_silence_and_duration() -> None:
    sr = 16000
    silence = np.zeros(sr, dtype=np.float32)
    tone = np.ones(sr, dtype=np.float32) * 0.2
    samples = np.concatenate([silence, tone, silence])
    trimmed = trim_silence(samples, sample_rate_hz=sr, threshold=0.01)
    assert trimmed.shape[0] < samples.shape[0]
    short = trim_duration(trimmed, sample_rate_hz=sr, max_duration_sec=0.25)
    assert short.shape[0] <= int(0.25 * sr)


def test_preprocessor_ok() -> None:
    wav = _sine(seconds=1.0)
    out = DefaultPreprocessor(AudioPreprocessingConfig(min_duration_sec=0.1)).transform(wav)
    assert out.sample_rate_hz == 16000
    assert out.duration_sec >= 0.1


def test_preprocessor_rejects_too_short() -> None:
    wav = Waveform(samples=np.zeros(10, dtype=np.float32), sample_rate_hz=16000)
    with pytest.raises(ValidationError):
        DefaultPreprocessor().transform(wav)


def test_soundfile_loader_roundtrip(tmp_path: Path) -> None:
    wav = _sine(seconds=0.5)
    path = tmp_path / "a.wav"
    sf.write(path, wav.samples, wav.sample_rate_hz)
    loaded = SoundFileLoader().load(path)
    assert loaded.sample_rate_hz == wav.sample_rate_hz
    assert loaded.samples.shape[0] > 0


def test_magic_byte_validator_wav() -> None:
    data = b"RIFF" + b"\x00" * 12
    MagicByteValidator().validate(
        UploadBlob(filename="a.wav", content_type="audio/wav", data=data, size_bytes=len(data)),
    )


def test_magic_byte_validator_rejects() -> None:
    data = b"XXXX"
    with pytest.raises(ValidationError):
        MagicByteValidator().validate(
            UploadBlob(filename="a.bin", content_type="audio/wav", data=data, size_bytes=4),
        )


def test_spectrogram_shapes() -> None:
    wav = _sine(seconds=0.5)
    spec = stft_magnitude(wav.samples)
    assert spec.ndim == 2
    mel = mel_spectrogram(wav.samples, sample_rate_hz=wav.sample_rate_hz)
    assert mel.shape[0] == 80


def test_augment_deterministic() -> None:
    wav = _sine(seconds=0.5)
    a = gain_augment(wav, gain_db=3.0, rng=np.random.default_rng(1))
    b = gain_augment(wav, gain_db=3.0, rng=np.random.default_rng(1))
    assert np.allclose(a.samples, b.samples)
    noisy = additive_noise_augment(wav, snr_db=20.0, rng=np.random.default_rng(2))
    assert noisy.samples.shape == wav.samples.shape


def test_pairing_helpers() -> None:
    clean = ClipMetadata(
        clip_id="c1",
        language=Language.HI,
        source=DatasetSource.KATHBATH,
        label=Label.REAL,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=16000,
        duration_sec=1.0,
        split=Split.TRAIN,
        dataset_source="kathbath",
    )
    pair = make_pair_id("c1")
    child = paired_clip_metadata(clean, compressed_clip_id="c1__opus")
    assert child.pair_id == pair
    assert child.compression_status is CompressionCondition.OPUS_WHATSAPP_SIM
