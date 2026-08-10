"""Streaming session manager stub (ROADMAP-055 / REQ-096)."""

from __future__ import annotations

from vaaniq.core.domain.entities import PredictionResult
from vaaniq.core.errors import NotImplementedInPhaseError


class StreamingSession:
    """Manage a live MediaRecorder inference session.

    TODO(ROADMAP-055): bind WindowBuffer + inference pipeline.
    """

    def __init__(self, session_id: str) -> None:
        """Create a session with ``session_id``."""
        self.session_id = session_id

    def ingest(self, chunk: bytes) -> PredictionResult | None:
        """Ingest audio chunk (deferred to ROADMAP-055)."""
        raise NotImplementedInPhaseError("ROADMAP-055", "StreamingSession.ingest")

    def finalize(self) -> PredictionResult:
        """Finalize session (deferred to ROADMAP-055)."""
        raise NotImplementedInPhaseError("ROADMAP-055", "StreamingSession.finalize")
