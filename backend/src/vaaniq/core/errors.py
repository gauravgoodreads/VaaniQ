"""VaaniQ exception hierarchy.

All project errors inherit from ``VaaniQError`` (vaaniq-core.mdc). Serves INFRA /
ROADMAP-003.
"""

from __future__ import annotations


class VaaniQError(Exception):
    """Root exception for all VaaniQ failures."""


class ConfigurationError(VaaniQError):
    """Invalid or incomplete configuration."""


class ValidationError(VaaniQError):
    """Input failed domain or upload validation (REQ-135)."""


class AudioDecodeError(VaaniQError):
    """Audio could not be decoded by primary or fallback loader (REQ-094)."""


class DatasetError(VaaniQError):
    """Dataset access, licence, or manifest failure (REQ-130)."""


class ModelNotReadyError(VaaniQError):
    """Requested model or artefact is missing or not loaded."""


class NotImplementedInPhaseError(VaaniQError):
    """Feature deferred to a named ROADMAP item.

    Args:
        roadmap_id: Identifier such as ``ROADMAP-025``.
        detail: Human-readable explanation.
    """

    def __init__(self, roadmap_id: str, detail: str) -> None:
        """Bind the roadmap reference and detail message.

        Args:
            roadmap_id: Identifier such as ``ROADMAP-025``.
            detail: Human-readable explanation.
        """
        self.roadmap_id = roadmap_id
        self.detail = detail
        super().__init__(f"{roadmap_id}: {detail}")


class PersistenceError(VaaniQError):
    """Database or object-store persistence failure."""


class CalibrationError(VaaniQError):
    """Calibration fit or transform failure (REQ-054)."""
