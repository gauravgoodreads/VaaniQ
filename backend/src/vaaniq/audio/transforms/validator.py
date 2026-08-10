"""Upload magic-byte validator stub (ROADMAP-057 / REQ-135)."""

from __future__ import annotations

from vaaniq.core.domain.entities import UploadBlob
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.audio_validator import AudioValidator


class MagicByteValidator(AudioValidator):
    """Validate MIME, magic bytes, duration, and size before decode.

    TODO(ROADMAP-057): enforce limits from ``AppConfig.api``.
    """

    def validate(self, upload: UploadBlob) -> None:
        """Validate ``upload`` (deferred to ROADMAP-057)."""
        raise NotImplementedInPhaseError("ROADMAP-057", "MagicByteValidator.validate")
