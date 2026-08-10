"""Streaming window buffer stub (ROADMAP-055 / REQ-096)."""

from __future__ import annotations

from vaaniq.core.domain.entities import Waveform
from vaaniq.core.errors import NotImplementedInPhaseError


class WindowBuffer:
    """Sliding-window PCM buffer for live inference.

    TODO(ROADMAP-055): config-driven window/hop (OQ-019).
    """

    def push(self, chunk: bytes) -> Waveform | None:
        """Append bytes; return a ready window or ``None`` (deferred)."""
        raise NotImplementedInPhaseError("ROADMAP-055", "WindowBuffer.push")

    def reset(self) -> None:
        """Clear buffer state (deferred to ROADMAP-055)."""
        raise NotImplementedInPhaseError("ROADMAP-055", "WindowBuffer.reset")
