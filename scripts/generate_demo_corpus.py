#!/usr/bin/env python3
"""Generate VaaniQ demo corpus with mic-realistic REAL vs TTS-like FAKE speech.

Real clips: irregular pitch, breath/room noise (closer to laptop mic).
Fake clips: stable pitch, metallic harmonics, AM flutter (TTS/clone cues).
Languages: hi / mr / ta with accent shifts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

LANGUAGES = ("hi", "mr", "ta")
LANG_FORMANTS: dict[str, tuple[float, float, float]] = {
    "hi": (720.0, 1240.0, 2450.0),
    "mr": (650.0, 1180.0, 2380.0),
    "ta": (780.0, 1320.0, 2550.0),
}
ACCENT_SHIFTS: tuple[tuple[float, float, float], ...] = (
    (0.0, 0.0, 0.0),
    (40.0, -30.0, 50.0),
    (-35.0, 45.0, -20.0),
    (25.0, 20.0, -40.0),
    (-20.0, -50.0, 60.0),
    (55.0, -15.0, 25.0),
    (-45.0, 35.0, -55.0),
    (15.0, -60.0, 40.0),
)


def _speech_like(
    *,
    seconds: float,
    sr: int,
    f0: float,
    formants: tuple[float, float, float],
    seed: int,
    fake: bool,
    hard: bool,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    t = np.arange(n, dtype=np.float64) / sr

    if fake:
        # Stable robotic F0 + metallic high harmonics (clone / TTS cue).
        fake_jitter = 0.022 if hard else 0.008
        f0_t = f0 * (1.0 + fake_jitter * np.sin(2 * np.pi * 6.0 * t))
        phase = 2 * np.pi * np.cumsum(f0_t) / sr
        buzz = np.sin(phase)
        max_harmonic = 6 if hard else 10
        for h in range(2, max_harmonic):
            buzz += ((0.38 if hard else 0.55) / h) * np.sin(h * phase)
        buzz += (
            (0.12 if hard else 0.32) * np.sin(11 * phase) * (1.0 + 0.4 * np.sin(2 * np.pi * 18 * t))
        )
        buzz += (0.06 if hard else 0.18) * np.sin(17 * phase)
        buzz *= 1.0 + (0.05 if hard else 0.12) * np.sin(2 * np.pi * 40 * t)
        env = 0.7 + 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 3.5 * t))
        room = 0.018 if hard else 0.004
        breath = 0.008 if hard else 0.0
    else:
        # Mic-realistic human-ish: pitch jitter, breath, room noise, softer harmonics.
        jitter = rng.normal(0.0, 0.025, size=n)
        # smooth jitter
        kernel = np.ones(64) / 64.0
        jitter = np.convolve(jitter, kernel, mode="same")
        f0_t = f0 * (1.0 + 0.04 * np.sin(2 * np.pi * 5.0 * t) + jitter)
        phase = 2 * np.pi * np.cumsum(np.maximum(f0_t, 40.0)) / sr
        buzz = np.sin(phase)
        for h in range(2, 5):
            buzz += (0.35 / h) * np.sin(h * phase + rng.uniform(0, 0.5))
        # syllable irregularity
        env = 0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * (1.6 + (seed % 7) * 0.11) * t))
        env *= 0.85 + 0.15 * rng.random(n)
        room = 0.016 if hard else 0.035
        breath = 0.008 if hard else 0.02
        if hard:
            # Clean, vocoder-like human speech without changing its real label.
            buzz += 0.08 * np.sin(9 * phase)

    sig = np.zeros(n, dtype=np.float64)
    for i, f in enumerate(formants):
        gain = (0.5 if fake else 0.62) / (i + 1)
        sig += gain * buzz * np.sin(2 * np.pi * f * t) * env

    # simple early reflection (room)
    delay = int(0.018 * sr)
    if delay < n:
        echo = np.zeros_like(sig)
        echo[delay:] = sig[:-delay] * (0.22 if not fake else 0.05)
        sig = sig + echo

    noise = rng.normal(0.0, room, size=n)
    if breath > 0:
        # breathy highband-ish noise shaped by envelope
        breath_n = rng.normal(0.0, breath, size=n) * env
        noise = noise + breath_n

    out = (sig + noise).astype(np.float32)
    # mic soft clip / AGC unevenness for real
    if not fake:
        out = np.tanh(out * 1.35).astype(np.float32)
    peak = float(np.max(np.abs(out))) or 1.0
    return (0.85 * out / peak).astype(np.float32)


def generate(root: Path, *, clips_per_lang: int, duration_sec: float, sr: int) -> Path:
    audio_dir = root / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for lang_i, lang in enumerate(LANGUAGES):
        base = LANG_FORMANTS[lang]
        for k in range(clips_per_lang):
            fake = k % 2 == 1
            label = "fake" if fake else "real"
            # Borderline clips (hard negatives) for realistic val error rates.
            hard = k % 9 == 0
            compression = "opus_whatsapp_sim" if k % 3 == 0 else "clean"
            clip_id = f"{lang}-{k}"
            shift = ACCENT_SHIFTS[k % len(ACCENT_SHIFTS)]
            formants = (
                max(200.0, base[0] + shift[0]),
                max(400.0, base[1] + shift[1]),
                max(800.0, base[2] + shift[2]),
            )
            f0 = 95.0 + (k % 12) * 9.5 + lang_i * 4.0 + (k % 3) * 3.0
            wav = _speech_like(
                seconds=duration_sec,
                sr=sr,
                f0=f0,
                formants=formants,
                seed=1000 + lang_i * 200 + k,
                fake=fake,
                hard=hard,
            )
            if compression == "opus_whatsapp_sim":
                step = max(1, sr // 8000)
                rough = wav[::step]
                up = np.repeat(rough, step)[: wav.shape[0]]
                wav = (0.9 * up + 0.1 * wav).astype(np.float32)
            rel = f"audio/{clip_id}.wav"
            path = root / rel
            sf.write(path, wav, sr)
            rows.append(
                {
                    "clip_id": clip_id,
                    "language": lang,
                    "label": label,
                    "compression_status": compression,
                    "sample_rate_hz": sr,
                    "duration_sec": duration_sec,
                    "split": "test" if k % 5 == 0 else ("val" if k % 5 == 1 else "train"),
                    "difficulty": "hard" if hard else "standard",
                    "dataset_source": "demo_corpus_mic_aware",
                    "uri": rel.replace("\\", "/"),
                }
            )
    manifest = root / "manifest.jsonl"
    with manifest.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    meta = {
        "languages": list(LANGUAGES),
        "clips_per_language": clips_per_lang,
        "duration_sec": duration_sec,
        "total_clips": len(rows),
        "total_hours": len(rows) * duration_sec / 3600.0,
        "note": "Multi-accent synthetic corpus (hi/mr/ta) for capstone training and demo.",
    }
    (root / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "demo_corpus",
    )
    parser.add_argument("--clips-per-lang", type=int, default=150)
    parser.add_argument("--duration-sec", type=float, default=12.0)
    parser.add_argument("--sample-rate", type=int, default=16000)
    args = parser.parse_args()
    generate(
        args.root,
        clips_per_lang=args.clips_per_lang,
        duration_sec=args.duration_sec,
        sr=args.sample_rate,
    )


if __name__ == "__main__":
    main()
