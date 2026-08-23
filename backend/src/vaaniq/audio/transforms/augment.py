"""Light config-driven audio augmentations (ROADMAP-020).

Bodies are minimal but typed and unit-tested; training loops come later.
"""

from __future__ import annotations

import numpy as np

from vaaniq.core.domain.entities import Float32Array, Waveform


def gain_augment(wav: Waveform, *, gain_db: float, rng: np.random.Generator) -> Waveform:
    """Apply a random gain within ±``gain_db``.

    Args:
        wav: Input waveform.
        gain_db: Max absolute gain in dB.
        rng: Numpy generator for determinism under ``--seed``.

    Returns:
        Augmented waveform (same sample rate).
    """
    if gain_db <= 0.0:
        return wav
    delta = float(rng.uniform(-gain_db, gain_db))
    scale = float(10.0 ** (delta / 20.0))
    samples: Float32Array = (wav.samples * np.float32(scale)).astype(np.float32)
    return Waveform(samples=samples, sample_rate_hz=wav.sample_rate_hz)


def additive_noise_augment(
    wav: Waveform,
    *,
    snr_db: float,
    rng: np.random.Generator,
) -> Waveform:
    """Add white noise at approximately ``snr_db`` relative to signal power.

    Args:
        wav: Input waveform.
        snr_db: Target signal-to-noise ratio in dB.
        rng: Numpy generator.

    Returns:
        Noisy waveform.
    """
    if wav.samples.size == 0:
        return wav
    power = float(np.mean(np.square(wav.samples)))
    if power <= 0.0:
        return wav
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.normal(0.0, np.sqrt(noise_power), size=wav.samples.shape).astype(np.float32)
    return Waveform(
        samples=(wav.samples + noise).astype(np.float32), sample_rate_hz=wav.sample_rate_hz
    )
