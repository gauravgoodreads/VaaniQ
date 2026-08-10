"""Speaker-disjoint split builder stub (ROADMAP-017 / REQ-099)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.types import Split


class SpeakerDisjointSplitter:
    """Write versioned speaker-disjoint train/val/test manifests.

    TODO(ROADMAP-017): enforce speaker disjointness; never compute splits on the fly.
    """

    def build(
        self,
        clips: Sequence[ClipMetadata],
        *,
        seed: int,
        destination: Path,
    ) -> Mapping[Split, Path]:
        """Build split manifests (deferred to ROADMAP-017)."""
        raise NotImplementedInPhaseError("ROADMAP-017", "SpeakerDisjointSplitter.build")
