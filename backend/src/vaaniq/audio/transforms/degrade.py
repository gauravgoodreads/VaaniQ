"""Waveform degradation for RQ1 robustness studies (ROADMAP-023).

Primary Opus path remains ``FFmpegOpusCompressor``. These operators cover
resample and packet-loss simulations when ffmpeg is unavailable (OQ-037/038).
"""

from __future__ import annotations

import numpy as np

from vaaniq.audio.transforms.ops import resample_linear
from vaaniq.core.domain.entities import Waveform


def resample_waveform(wav: Waveform, target_hz: int) -> Waveform:
    """Resample ``wav`` to ``target_hz`` then back to original rate.

    Round-trip matches a delivery path that resamples then restores 16 kHz
    (proposal p.6 WhatsApp-style resampling). Serves RQ1.

    Args:
        wav: Input waveform.
        target_hz: Intermediate sample rate.

    Returns:
        Waveform at the original sample rate after round-trip resample.
    """
    mid = resample_linear(wav.samples, src_hz=wav.sample_rate_hz, dst_hz=target_hz)
    back = resample_linear(mid, src_hz=target_hz, dst_hz=wav.sample_rate_hz)
    return Waveform(samples=back, sample_rate_hz=wav.sample_rate_hz)


def simulate_packet_loss(
    wav: Waveform,
    *,
    loss_fraction: float,
    rng: np.random.Generator,
    frame_ms: int = 20,
) -> Waveform:
    """Zero random frames to simulate packet loss (ASSUMPTION: OQ-037).

    Args:
        wav: Input waveform.
        loss_fraction: Fraction of frames to drop in ``[0, 1]``.
        rng: Deterministic generator.
        frame_ms: Frame length in milliseconds (VoIP-typical 20 ms).

    Returns:
        Degraded waveform at the same rate.
    """
    samples = np.asarray(wav.samples, dtype=np.float32).copy()
    if loss_fraction <= 0.0 or samples.size == 0:
        return Waveform(samples=samples, sample_rate_hz=wav.sample_rate_hz)
    hop = max(1, int(wav.sample_rate_hz * frame_ms / 1000.0))
    n_frames = max(1, samples.size // hop)
    n_drop = round(n_frames * min(1.0, loss_fraction))
    if n_drop <= 0:
        return Waveform(samples=samples, sample_rate_hz=wav.sample_rate_hz)
    dropped = rng.choice(n_frames, size=min(n_drop, n_frames), replace=False)
    for idx in dropped:
        start = int(idx) * hop
        samples[start : start + hop] = 0.0
    return Waveform(samples=samples, sample_rate_hz=wav.sample_rate_hz)
