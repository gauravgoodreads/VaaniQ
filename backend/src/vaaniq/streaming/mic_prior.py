"""Laptop-mic domain prior for live speech (REQ-096).

Studio Kathbath vs IndicSynth is in-domain. A laptop microphone is not:
the Baseline V1 head often scores live human speech as fake. Live/mic
captures therefore require stronger fake evidence than file uploads.
# ASSUMPTION: OQ-live-mic-threshold — demo policy, not a frozen eval number.
"""

from __future__ import annotations

import numpy as np

from vaaniq.core.types import Label

LIVE_FAKE_THRESHOLD = 0.85
LIVE_SURE_FAKE = 0.92
MIN_RMS = 0.012
FAKE_STREAK = 2


def speech_energy_cues(samples: np.ndarray, sample_rate_hz: int) -> tuple[float, float]:
    """Return (energy dynamics, 10th-percentile frame energy)."""
    flat = np.asarray(samples, dtype=np.float32).reshape(-1)
    hop = max(1, int(sample_rate_hz * 0.02))
    if flat.size < hop * 8:
        return 0.0, 0.0
    frames = flat[: flat.size - (flat.size % hop)].reshape(-1, hop)
    energies = np.mean(np.square(frames), axis=1)
    dyn = float(np.std(energies) / (np.mean(energies) + 1e-8))
    noise_floor = float(np.percentile(energies, 10))
    return dyn, noise_floor


def adjust_fake_p_for_mic(
    fake_p: float,
    samples: np.ndarray,
    sample_rate_hz: int,
) -> float:
    """Nudge P(fake) down when the clip looks like room/mic speech, not TTS."""
    dyn, noise_floor = speech_energy_cues(samples, sample_rate_hz)
    adjusted = float(fake_p)
    if dyn > 0.35:
        adjusted = max(0.0, adjusted - 0.18)
    if noise_floor > 1e-5:
        adjusted = max(0.0, adjusted - 0.08)
    return float(np.clip(adjusted, 0.0, 1.0))


def label_from_fake_p(
    fake_p: float,
    *,
    live_mic: bool,
    samples: np.ndarray | None = None,
    sample_rate_hz: int = 16000,
) -> tuple[Label, float]:
    """Map P(fake) to a label. File uploads stay at 0.5; live mic is conservative.

    Returns:
        (label, adjusted_fake_p used for the decision)
    """
    if not live_mic:
        return (Label.FAKE if fake_p >= 0.5 else Label.REAL, fake_p)
    flat = np.asarray(samples if samples is not None else [], dtype=np.float32)
    adjusted = adjust_fake_p_for_mic(fake_p, flat, sample_rate_hz)
    dyn, _noise_floor = speech_energy_cues(flat, sample_rate_hz)
    looks_like_room_mic = dyn > 0.28
    if looks_like_room_mic and adjusted < LIVE_SURE_FAKE:
        return Label.REAL, adjusted
    if adjusted >= LIVE_FAKE_THRESHOLD:
        return Label.FAKE, adjusted
    return Label.REAL, adjusted


def is_live_mic_source(source: str, filename: str) -> bool:
    """True when the clip was captured from the browser microphone."""
    src = source.strip().lower()
    name = filename.strip().lower()
    if src in {"mic", "live", "microphone"}:
        return True
    return name.startswith("live-") or name.startswith("vaaniq-recording-")
