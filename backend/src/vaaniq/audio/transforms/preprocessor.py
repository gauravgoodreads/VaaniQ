"""Default preprocessor (ROADMAP-020 / REQ-098)."""

from __future__ import annotations

import structlog

from vaaniq.audio.transforms.ops import apply_waveform_ops
from vaaniq.config.domains import AudioPreprocessingConfig
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import ValidationError
from vaaniq.core.ports.preprocessor import Preprocessor

log = structlog.get_logger(__name__)


class DefaultPreprocessor(Preprocessor):
    """Resample, trim, and normalize waveforms from config.

    Serves REQ-098. Defaults match ``configs/audio/preprocessing.yaml``
    (ASSUMPTION: OQ-007).
    """

    def __init__(self, config: AudioPreprocessingConfig | None = None) -> None:
        """Bind preprocessing config.

        Args:
            config: Optional typed config; defaults to YAML-equivalent defaults.
        """
        self._config = config or AudioPreprocessingConfig()

    def transform(self, wav: Waveform) -> Waveform:
        """Preprocess ``wav`` to the configured sample rate and loudness.

        Args:
            wav: Input waveform.

        Returns:
            Preprocessed waveform.

        Raises:
            ValidationError: If duration is outside configured bounds after
                transforms.
        """
        cfg = self._config
        out = apply_waveform_ops(
            wav,
            target_hz=cfg.sample_rate_hz,
            mono=cfg.mono,
            do_trim_silence=cfg.trim_silence,
            do_peak_norm=cfg.normalize_peak,
            target_peak=cfg.target_peak,
            max_duration_sec=float(cfg.max_duration_sec),
        )
        if out.duration_sec < cfg.min_duration_sec:
            raise ValidationError(
                f"audio duration {out.duration_sec:.3f}s below min {cfg.min_duration_sec}s",
            )
        log.info(
            "waveform_preprocessed",
            src_hz=wav.sample_rate_hz,
            dst_hz=out.sample_rate_hz,
            duration_sec=out.duration_sec,
        )
        return out
