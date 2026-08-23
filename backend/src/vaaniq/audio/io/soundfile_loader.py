"""SoundFile-based audio loader (ROADMAP-019 / REQ-094)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import structlog

from vaaniq.audio.transforms.ops import to_mono
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import AudioDecodeError
from vaaniq.core.ports.audio_loader import AudioLoader

log = structlog.get_logger(__name__)


class SoundFileLoader(AudioLoader):
    """Primary decoder via soundfile/libsndfile (REQ-094)."""

    def load(self, uri: str | Path) -> Waveform:
        """Load audio from ``uri`` and return a mono float32 waveform.

        Args:
            uri: Filesystem path to an audio file.

        Returns:
            Mono ``Waveform``.

        Raises:
            AudioDecodeError: If the file cannot be decoded.
        """
        path = Path(uri)
        try:
            import soundfile as sf
        except ImportError as exc:  # pragma: no cover - dependency gate
            raise AudioDecodeError("soundfile package is not installed") from exc
        try:
            data, sr = sf.read(str(path), always_2d=True, dtype="float32")
        except Exception as exc:
            raise AudioDecodeError(f"soundfile failed to decode {path}") from exc
        samples = to_mono(np.asarray(data, dtype=np.float32))
        log.info("audio_loaded", path=str(path), sr=int(sr), n_samples=int(samples.shape[0]))
        return Waveform(samples=samples, sample_rate_hz=int(sr))
