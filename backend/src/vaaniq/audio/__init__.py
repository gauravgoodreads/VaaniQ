"""Audio package public exports (Phase 1 stubs)."""

from __future__ import annotations

from vaaniq.audio.compression.ffmpeg_opus import FFmpegOpusCompressor
from vaaniq.audio.io.fallback_loader import FallbackDecoderLoader
from vaaniq.audio.io.soundfile_loader import SoundFileLoader
from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.audio.transforms.validator import MagicByteValidator

__all__ = [
    "DefaultPreprocessor",
    "FFmpegOpusCompressor",
    "FallbackDecoderLoader",
    "MagicByteValidator",
    "SoundFileLoader",
]
