"""Fallback audio decoder via ffmpeg CLI (ROADMAP-019 / REQ-094)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import structlog

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import AudioDecodeError
from vaaniq.core.ports.audio_loader import AudioLoader

log = structlog.get_logger(__name__)


class FallbackDecoderLoader(AudioLoader):
    """Secondary decoder using ffmpeg PCM dump when primary decode fails.

    Chains after ``SoundFileLoader`` on ``AudioDecodeError`` (REQ-094).
    """

    def __init__(self, *, ffmpeg_bin: str = "ffmpeg", sample_rate_hz: int = 16000) -> None:
        """Bind ffmpeg binary and target rate.

        Args:
            ffmpeg_bin: ffmpeg executable name or path.
            sample_rate_hz: Output PCM sample rate (ASSUMPTION: OQ-007).
        """
        self._ffmpeg_bin = ffmpeg_bin
        self._sample_rate_hz = sample_rate_hz

    def load(self, uri: str | Path) -> Waveform:
        """Decode ``uri`` to mono PCM via ffmpeg.

        Args:
            uri: Filesystem path.

        Returns:
            Mono ``Waveform`` at configured sample rate.

        Raises:
            AudioDecodeError: If ffmpeg is missing or decode fails.
        """
        path = Path(uri)
        ffmpeg = shutil.which(self._ffmpeg_bin)
        if ffmpeg is None:
            raise AudioDecodeError("ffmpeg binary not found on PATH")
        with tempfile.TemporaryDirectory(prefix="vaaniq_fb_") as tmp:
            out_path = Path(tmp) / "out.f32"
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(path),
                "-ac",
                "1",
                "-ar",
                str(self._sample_rate_hz),
                "-f",
                "f32le",
                str(out_path),
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            except OSError as exc:
                raise AudioDecodeError("failed to spawn ffmpeg") from exc
            if proc.returncode != 0 or not out_path.is_file():
                raise AudioDecodeError(f"ffmpeg decode failed for {path}")
            raw = out_path.read_bytes()
        samples = np.frombuffer(raw, dtype=np.float32).copy()
        log.info(
            "audio_loaded_ffmpeg_fallback",
            path=str(path),
            sr=self._sample_rate_hz,
            n_samples=int(samples.shape[0]),
        )
        return Waveform(samples=samples, sample_rate_hz=self._sample_rate_hz)
