"""Spectrogram and mel utilities (ROADMAP-020 / explainability prep).

Pure numpy implementations — no training code.
"""

from __future__ import annotations

import numpy as np

from vaaniq.core.domain.entities import Float32Array


def stft_magnitude(
    samples: Float32Array,
    *,
    n_fft: int = 512,
    hop_length: int = 160,
) -> Float32Array:
    """Compute a simple real STFT magnitude spectrogram.

    ASSUMPTION: OQ-034 — spectrogram path aligned for later Grad-CAM; FFT
    sizes are provisional until model-input lock.

    Args:
        samples: Mono float32 waveform.
        n_fft: FFT size.
        hop_length: Hop between frames.

    Returns:
        Array shaped ``(n_freq, n_frames)``.
    """
    if samples.size == 0:
        return np.zeros((n_fft // 2 + 1, 0), dtype=np.float32)
    window = np.hanning(n_fft).astype(np.float32)
    if samples.shape[0] < n_fft:
        padded = np.zeros(n_fft, dtype=np.float32)
        padded[: samples.shape[0]] = samples
        frame = padded * window
        spec = np.fft.rfft(frame)
        return np.abs(spec).astype(np.float32)[:, np.newaxis]
    n_frames = 1 + (samples.shape[0] - n_fft) // hop_length
    out = np.empty((n_fft // 2 + 1, n_frames), dtype=np.float32)
    for i in range(n_frames):
        start = i * hop_length
        frame = samples[start : start + n_fft] * window
        out[:, i] = np.abs(np.fft.rfft(frame)).astype(np.float32)
    return out


def mel_filterbank(
    *,
    n_fft: int,
    sample_rate_hz: int,
    n_mels: int = 80,
) -> Float32Array:
    """Build a triangular mel filterbank matrix.

    Args:
        n_fft: FFT size.
        sample_rate_hz: Audio sample rate.
        n_mels: Number of mel bands.

    Returns:
        Filterbank of shape ``(n_mels, n_fft // 2 + 1)``.
    """
    # ASSUMPTION: OQ-013-adjacent — mel params provisional for visualization.
    n_freqs = n_fft // 2 + 1
    max_mel = 2595.0 * np.log10(1.0 + (sample_rate_hz / 2.0) / 700.0)
    mel_points = np.linspace(0.0, max_mel, n_mels + 2)
    hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
    bins = np.floor((n_fft + 1) * hz_points / sample_rate_hz).astype(np.int64)
    fb = np.zeros((n_mels, n_freqs), dtype=np.float32)
    for m in range(1, n_mels + 1):
        left, center, right = int(bins[m - 1]), int(bins[m]), int(bins[m + 1])
        left = max(0, min(left, n_freqs - 1))
        center = max(0, min(center, n_freqs - 1))
        right = max(0, min(right, n_freqs - 1))
        if center > left:
            fb[m - 1, left:center] = (np.arange(left, center) - left) / max(1, center - left)
        if right > center:
            fb[m - 1, center:right] = (right - np.arange(center, right)) / max(1, right - center)
    return fb


def mel_spectrogram(
    samples: Float32Array,
    *,
    sample_rate_hz: int,
    n_fft: int = 512,
    hop_length: int = 160,
    n_mels: int = 80,
) -> Float32Array:
    """Compute a mel spectrogram via STFT magnitude x filterbank.

    Args:
        samples: Mono float32 waveform.
        sample_rate_hz: Sample rate.
        n_fft: FFT size.
        hop_length: Hop length.
        n_mels: Mel bands.

    Returns:
        Array shaped ``(n_mels, n_frames)``.
    """
    mag = stft_magnitude(samples, n_fft=n_fft, hop_length=hop_length)
    fb = mel_filterbank(n_fft=n_fft, sample_rate_hz=sample_rate_hz, n_mels=n_mels)
    return (fb @ mag).astype(np.float32)
