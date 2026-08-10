"""Upload validation port (REQ-135)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vaaniq.core.domain.entities import UploadBlob


class AudioValidator(ABC):
    """Validate uploads before persistence or decode.

    Serves REQ-135 (MIME, magic bytes, duration, file size). Implementation:
    MagicByteValidator (ROADMAP-057).
    """

    @abstractmethod
    def validate(self, upload: UploadBlob) -> None:
        """Validate ``upload`` in place.

        Args:
            upload: Raw upload blob.

        Raises:
            ValidationError: If any check fails.
        """
