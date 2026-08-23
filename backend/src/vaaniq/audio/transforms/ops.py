"""Pure waveform transform operators (ROADMAP-020 / REQ-098).

Independently testable; used by ``DefaultPreprocessor``.
"""

from __future__ import annotations

import numpy as np

from vaaniq.core.domain.entities import Float32Array, Waveform


def to_mono(samples: Float32Array) -> Float32Array:
    """Collapse multi-channel samples to mono by mean across channels.

    Args:
        samples: Shape ``(n,)`` or ``(n, channels)``.

    Returns:
        Mono float32 vector.
    """
    if samples.ndim == 1:
        return np.asarray(samples, dtype=np.float32)
    if samples.ndim == 2:
        return np.asarray(np.mean(samples, axis=1), dtype=np.float32)
    msg = f"unsupported sample ndim={samples.ndim}"
    raise ValueError(msg)


def resample_linear(samples: Float32Array, *, src_hz: int, dst_hz: int) -> Float32Array:
    """Resample mono audio with linear interpolation.

    ASSUMPTION: OQ-007 — default pipeline targets 16 kHz; higher-quality
    resamplers may replace this later without changing the Preprocessor port.

    Args:
        samples: Mono float32 samples.
        src_hz: Source sample rate.
        dst_hz: Destination sample rate.

    Returns:
        Resampled mono float32 samples.
    """
    if src_hz <= 0 or dst_hz <= 0:
        msg = "sample rates must be positive"
        raise ValueError(msg)
    if src_hz == dst_hz or samples.size == 0:
        return np.asarray(samples, dtype=np.float32)
    duration = float(samples.shape[0]) / float(src_hz)
    n_out = max(1, round(duration * float(dst_hz)))
    x_old = np.linspace(0.0, 1.0, num=samples.shape[0], endpoint=False, dtype=np.float64)
    x_new = np.linspace(0.0, 1.0, num=n_out, endpoint=False, dtype=np.float64)
    out = np.interp(x_new, x_old, samples.astype(np.float64))
    return out.astype(np.float32)


def peak_normalize(samples: Float32Array, *, target_peak: float = 0.95) -> Float32Array:
    """Scale so max abs sample equals ``target_peak`` (no-op if silent).

    Args:
        samples: Mono float32 samples.
        target_peak: Desired peak magnitude in ``(0, 1]``.

    Returns:
        Peak-normalized samples.
    """
    if target_peak <= 0.0:
        msg = "target_peak must be positive"
        raise ValueError(msg)
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    if peak <= 0.0:
        return np.asarray(samples, dtype=np.float32)
    scale = float(target_peak) / peak
    return (samples.astype(np.float32) * np.float32(scale)).astype(np.float32)


def trim_silence(
    samples: Float32Array,
    *,
    sample_rate_hz: int,
    threshold: float = 0.01,
    frame_ms: float = 20.0,
) -> Float32Array:
    """Trim leading/trailing frames below ``threshold`` RMS.

    Args:
        samples: Mono float32 samples.
        sample_rate_hz: Sample rate for frame sizing.
        threshold: RMS threshold for "silence".
        frame_ms: Frame length in milliseconds.

    Returns:
        Trimmed samples (original if entirely below threshold).
    """
    if samples.size == 0 or sample_rate_hz <= 0:
        return np.asarray(samples, dtype=np.float32)
    frame = max(1, int(sample_rate_hz * frame_ms / 1000.0))
    n_frames = int(np.ceil(samples.shape[0] / frame))
    padded = np.zeros(n_frames * frame, dtype=np.float32)
    padded[: samples.shape[0]] = samples
    frames = padded.reshape(n_frames, frame)
    rms = np.sqrt(np.mean(np.square(frames), axis=1))
    active = np.where(rms >= threshold)[0]
    if active.size == 0:
        return np.asarray(samples, dtype=np.float32)
    start = int(active[0]) * frame
    end = min(samples.shape[0], (int(active[-1]) + 1) * frame)
    return samples[start:end].astype(np.float32)


def trim_duration(
    samples: Float32Array,
    *,
    sample_rate_hz: int,
    max_duration_sec: float,
) -> Float32Array:
    """Truncate waveform to ``max_duration_sec``.

    Args:
        samples: Mono float32 samples.
        sample_rate_hz: Sample rate.
        max_duration_sec: Maximum kept duration.

    Returns:
        Possibly truncated samples.
    """
    if max_duration_sec <= 0 or sample_rate_hz <= 0:
        return np.asarray(samples, dtype=np.float32)
    max_n = int(max_duration_sec * sample_rate_hz)
    if samples.shape[0] <= max_n:
        return np.asarray(samples, dtype=np.float32)
    return samples[:max_n].astype(np.float32)


def estimate_noise_floor(samples: Float32Array, *, percentile: float = 10.0) -> float:
    """Estimate a simple noise-floor magnitude via low RMS percentile.

    Args:
        samples: Mono float32 samples.
        percentile: Percentile of absolute samples used as floor proxy.

    Returns:
        Non-negative float estimate.
    """
    if samples.size == 0:
        return 0.0
    return float(np.percentile(np.abs(samples), percentile))


def apply_waveform_ops(
    wav: Waveform,
    *,
    target_hz: int,
    mono: bool,
    do_trim_silence: bool,
    do_peak_norm: bool,
    target_peak: float,
    max_duration_sec: float,
) -> Waveform:
    """Apply the standard preprocess chain to ``wav``.

    Args:
        wav: Input waveform.
        target_hz: Destination sample rate.
        mono: Force mono (always applied if multi-channel array sneaks in).
        do_trim_silence: Whether to trim silence.
        do_peak_norm: Whether to peak-normalize.
        target_peak: Peak target when normalizing.
        max_duration_sec: Max duration truncate.

    Returns:
        Transformed waveform at ``target_hz``.
    """
    samples = to_mono(wav.samples) if mono else np.asarray(wav.samples, dtype=np.float32)
    samples = resample_linear(samples, src_hz=wav.sample_rate_hz, dst_hz=target_hz)
    if do_trim_silence:
        samples = trim_silence(samples, sample_rate_hz=target_hz)
    samples = trim_duration(samples, sample_rate_hz=target_hz, max_duration_sec=max_duration_sec)
    if do_peak_norm:
        samples = peak_normalize(samples, target_peak=target_peak)
    return Waveform(samples=samples, sample_rate_hz=target_hz)
