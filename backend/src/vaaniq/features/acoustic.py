"""Shared acoustic embedding used for train + inference + live (no HF weights required)."""

from __future__ import annotations

import numpy as np

from vaaniq.core.domain.entities import Waveform


def acoustic_embedding(wav: Waveform, *, dim: int = 1024) -> np.ndarray:
    """Build a rich 1024-D acoustic vector sensitive to voice / accent / synthesis cues.

    Features pack time-domain stats, zero-crossing, spectral shape, mel-ish bands,
    and harmonic roughness — enough for a NumPy AASIST head to separate real vs
    synthetic demo speech and transfer across hi/mr/ta accent variants.
    """
    samples = np.asarray(wav.samples, dtype=np.float32).reshape(-1)
    vec = np.zeros(dim, dtype=np.float32)
    if samples.size == 0:
        return vec

    # --- time domain (0..15) ---
    vec[0] = float(np.mean(samples))
    vec[1] = float(np.std(samples))
    vec[2] = float(np.max(samples))
    vec[3] = float(np.min(samples))
    vec[4] = float(np.mean(np.abs(samples)))
    vec[5] = float(np.mean(np.square(samples)))
    zc = np.mean(np.abs(np.diff(np.signbit(samples)).astype(np.float32)))
    vec[6] = float(zc)
    # short-time energy variance (syllable / cadence proxy)
    hop = max(1, int(wav.sample_rate_hz * 0.02))
    if samples.size >= hop * 4:
        frames = samples[: samples.size - (samples.size % hop)].reshape(-1, hop)
        energies = np.mean(np.square(frames), axis=1)
        vec[7] = float(np.std(energies))
        vec[8] = float(np.mean(energies))
        vec[9] = float(np.percentile(energies, 90))

    # --- spectrum (16..527) ---
    n_fft = min(2048, samples.size)
    spec = np.abs(np.fft.rfft(samples[:n_fft] * np.hanning(n_fft))).astype(np.float32)
    spec_n = spec / (float(np.max(spec)) + 1e-8)
    n = min(512, spec_n.size)
    vec[16 : 16 + n] = spec_n[:n]

    # spectral centroid / bandwidth / rolloff
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / max(wav.sample_rate_hz, 1))
    denom = float(np.sum(spec)) + 1e-8
    centroid = float(np.sum(freqs * spec) / denom)
    vec[10] = centroid / 8000.0
    vec[11] = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * spec) / denom) / 8000.0)
    cum = np.cumsum(spec)
    roll_idx = int(np.searchsorted(cum, 0.85 * cum[-1]))
    vec[12] = float(freqs[min(roll_idx, freqs.size - 1)] / 8000.0)

    # --- mel-ish log bands (528..655) ---
    n_bands = 64
    edges = np.linspace(0, spec.size - 1, n_bands + 1).astype(int)
    for i in range(n_bands):
        a, b = edges[i], max(edges[i] + 1, edges[i + 1])
        band = spec[a:b]
        vec[528 + i] = float(np.log1p(np.mean(band)))

    # --- harmonic roughness / synthesis cue (656..687) ---
    if spec.size > 40:
        diffs = np.diff(spec[:256])
        vec[656] = float(np.mean(np.abs(diffs)))
        vec[657] = float(np.std(diffs))
        # peakiness
        peaks = spec[1:-1] > spec[:-2]
        peaks &= spec[1:-1] > spec[2:]
        vec[658] = float(np.mean(peaks.astype(np.float32)))

    # L2 normalize for stable AASIST training
    norm = float(np.linalg.norm(vec)) + 1e-8
    return (vec / norm).astype(np.float32)
