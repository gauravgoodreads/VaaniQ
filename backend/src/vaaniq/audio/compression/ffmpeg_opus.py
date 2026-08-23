"""FFmpeg Opus compressor (ROADMAP-021 / REQ-113).

ASSUMPTION: OQ-007 — Opus 16 kbps VoIP-ish, 16 kHz mono OGG/Opus.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import structlog

from vaaniq.audio.compression.metadata import CompressionMetadata
from vaaniq.audio.compression.pairing import make_pair_id
from vaaniq.audio.io.soundfile_loader import SoundFileLoader
from vaaniq.config.domains import AudioCompressionConfig
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import AudioDecodeError, VaaniQError
from vaaniq.core.ports.compressor import Compressor

log = structlog.get_logger(__name__)


class CompressionError(VaaniQError):
    """Opus compression failed (ffmpeg missing or non-zero exit)."""


class FFmpegOpusCompressor(Compressor):
    """WhatsApp-style Opus compression via ffmpeg CLI (REQ-113)."""

    def __init__(
        self,
        config: AudioCompressionConfig | None = None,
        *,
        ffmpeg_bin: str = "ffmpeg",
    ) -> None:
        """Bind compression config and ffmpeg binary.

        Args:
            config: Typed compression config (defaults match YAML).
            ffmpeg_bin: ffmpeg executable.
        """
        self._config = config or AudioCompressionConfig()
        self._ffmpeg_bin = ffmpeg_bin
        self._loader = SoundFileLoader()

    def compress(self, wav: Waveform, cfg: Mapping[str, str]) -> Waveform:
        """Compress ``wav`` to Opus and re-decode to waveform.

        Args:
            wav: Clean input waveform.
            cfg: String overrides (``bitrate_kbps``, ``application``, ...).

        Returns:
            Decoded compressed waveform at configured sample rate.

        Raises:
            CompressionError: If ffmpeg is unavailable or fails.
        """
        bitrate = int(cfg.get("bitrate_kbps", str(self._config.bitrate_kbps)))
        application = cfg.get("application", self._config.application)
        return self._compress_at_bitrate(wav, bitrate_kbps=bitrate, application=application)

    def compress_with_metadata(
        self,
        wav: Waveform,
        *,
        parent_clip_id: str,
        bitrate_kbps: int | None = None,
    ) -> tuple[Waveform, CompressionMetadata]:
        """Compress and return waveform plus compression metadata.

        Args:
            wav: Clean waveform.
            parent_clip_id: Clean clip id for pair mapping.
            bitrate_kbps: Optional bitrate override.

        Returns:
            Compressed waveform and ``CompressionMetadata``.
        """
        br = bitrate_kbps if bitrate_kbps is not None else self._config.bitrate_kbps
        out = self._compress_at_bitrate(
            wav,
            bitrate_kbps=br,
            application=self._config.application,
        )
        pair_id = make_pair_id(parent_clip_id)
        child_id = f"{parent_clip_id}__opus_{br}k"
        ratio = float(wav.samples.nbytes) / float(max(1, out.samples.nbytes))
        loss = self._signal_loss_db(wav, out)
        meta = CompressionMetadata(
            pair_id=pair_id,
            parent_clip_id=parent_clip_id,
            child_clip_id=child_id,
            codec=self._config.codec,
            bitrate_kbps=br,
            quality=self._config.application,
            sample_rate_hz=self._config.sample_rate_hz,
            channels=self._config.channels,
            container=self._config.container,
            compression_ratio=ratio,
            signal_loss_db=loss,
        )
        log.info(
            "opus_compressed",
            pair_id=pair_id,
            bitrate_kbps=br,
            compression_ratio=ratio,
            signal_loss_db=loss,
        )
        return out, meta

    def bitrate_ladder(
        self, wav: Waveform, *, parent_clip_id: str
    ) -> Sequence[tuple[Waveform, CompressionMetadata]]:
        """Generate optional multi-bitrate Opus versions (OQ-012 SHOULD).

        Args:
            wav: Clean waveform.
            parent_clip_id: Parent clip id.

        Returns:
            List of (waveform, metadata) for each ladder bitrate when enabled;
            otherwise a single primary bitrate result.
        """
        rates = (
            list(self._config.bitrate_ladder_kbps)
            if self._config.enable_bitrate_ladder
            else [self._config.bitrate_kbps]
        )
        results: list[tuple[Waveform, CompressionMetadata]] = []
        for br in rates:
            results.append(
                self.compress_with_metadata(wav, parent_clip_id=parent_clip_id, bitrate_kbps=br),
            )
        return results

    def _compress_at_bitrate(
        self,
        wav: Waveform,
        *,
        bitrate_kbps: int,
        application: str,
    ) -> Waveform:
        ffmpeg = shutil.which(self._ffmpeg_bin)
        if ffmpeg is None:
            raise CompressionError("ffmpeg binary not found on PATH")
        with tempfile.TemporaryDirectory(prefix="vaaniq_opus_") as tmp:
            tmp_path = Path(tmp)
            pcm_path = tmp_path / "in.f32"
            opus_path = tmp_path / f"out.{self._config.container}"
            wav.samples.astype(np.float32).tofile(pcm_path)
            cmd = [
                ffmpeg,
                "-y",
                "-f",
                "f32le",
                "-ar",
                str(wav.sample_rate_hz),
                "-ac",
                "1",
                "-i",
                str(pcm_path),
                "-c:a",
                self._config.codec,
                "-b:a",
                f"{bitrate_kbps}k",
                "-application",
                application,
                "-ar",
                str(self._config.sample_rate_hz),
                "-ac",
                str(self._config.channels),
                str(opus_path),
            ]
            try:
                proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            except OSError as exc:
                raise CompressionError("failed to spawn ffmpeg") from exc
            if proc.returncode != 0 or not opus_path.is_file():
                raise CompressionError("ffmpeg opus encode failed")
            try:
                return self._loader.load(opus_path)
            except AudioDecodeError:
                # OGG/Opus may need fallback decode path
                from vaaniq.audio.io.fallback_loader import FallbackDecoderLoader

                return FallbackDecoderLoader(
                    ffmpeg_bin=self._ffmpeg_bin,
                    sample_rate_hz=self._config.sample_rate_hz,
                ).load(opus_path)

    @staticmethod
    def _signal_loss_db(clean: Waveform, compressed: Waveform) -> float:
        """Approximate RMS loss between clean and compressed (dB)."""
        n = min(clean.samples.shape[0], compressed.samples.shape[0])
        if n == 0:
            return 0.0
        a = clean.samples[:n]
        b = compressed.samples[:n]
        # Align lengths only; rates may differ slightly after codec
        err = a - b[: a.shape[0]] if a.shape[0] == b.shape[0] else a - np.resize(b, a.shape)
        mse = float(np.mean(np.square(err)))
        if mse <= 1e-12:
            return 0.0
        return float(10.0 * np.log10(mse + 1e-12))
