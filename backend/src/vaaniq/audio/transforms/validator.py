"""Upload magic-byte / size validator (ROADMAP-057 / REQ-135).

Implemented early so the audio pipeline can reject bad uploads before decode.
"""

from __future__ import annotations

import structlog

from vaaniq.core.domain.entities import UploadBlob
from vaaniq.core.errors import ValidationError
from vaaniq.core.ports.audio_validator import AudioValidator

log = structlog.get_logger(__name__)

# ASSUMPTION: upload limits provisional until AppConfig.api wires through DI.
_DEFAULT_MAX_BYTES = 25 * 1024 * 1024
_WAV_MAGIC = b"RIFF"
_OGG_MAGIC = b"OggS"
_FLAC_MAGIC = b"fLaC"
_ALLOWED_CONTENT_TYPES = frozenset(
    {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/ogg",
        "audio/opus",
        "audio/flac",
        "audio/mpeg",
        "application/octet-stream",
    },
)


class MagicByteValidator(AudioValidator):
    """Validate MIME, magic bytes, and size before decode (REQ-135)."""

    def __init__(self, *, max_bytes: int = _DEFAULT_MAX_BYTES) -> None:
        """Bind size limit.

        Args:
            max_bytes: Maximum accepted upload size.
        """
        self._max_bytes = max_bytes

    def validate(self, upload: UploadBlob) -> None:
        """Validate ``upload`` metadata and magic bytes.

        Args:
            upload: Raw upload blob.

        Raises:
            ValidationError: On MIME, size, or magic mismatch.
        """
        if upload.size_bytes <= 0 or upload.size_bytes > self._max_bytes:
            raise ValidationError("upload size out of allowed bounds")
        if len(upload.data) != upload.size_bytes:
            raise ValidationError("upload size_bytes does not match data length")
        if upload.content_type not in _ALLOWED_CONTENT_TYPES:
            raise ValidationError(f"unsupported content_type={upload.content_type}")
        if not self._magic_ok(upload.data):
            raise ValidationError("audio magic bytes not recognized")
        log.info(
            "upload_validated",
            filename=upload.filename,
            size_bytes=upload.size_bytes,
            content_type=upload.content_type,
        )

    @staticmethod
    def _magic_ok(data: bytes) -> bool:
        if len(data) < 4:
            return False
        head = data[:4]
        if head in (_WAV_MAGIC, _OGG_MAGIC, _FLAC_MAGIC):
            return True
        # MP3 frame sync or ID3 tag
        if data[:3] == b"ID3":
            return True
        return data[0] == 0xFF and (data[1] & 0xE0) == 0xE0
