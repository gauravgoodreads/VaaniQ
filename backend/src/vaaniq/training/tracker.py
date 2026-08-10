"""File-based experiment tracker stub (ROADMAP-030 / REQ-137)."""

from __future__ import annotations

from collections.abc import Mapping

from vaaniq.core.domain.entities import ExperimentManifest
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.experiment_tracker import ExperimentTracker


class FileExperimentTracker(ExperimentTracker):
    """Log metrics and manifests to the local experiment tree.

    TODO(ROADMAP-030): write under research/experiments/.
    """

    def log_metric(
        self,
        name: str,
        value: float,
        *,
        dims: Mapping[str, str] | None = None,
    ) -> None:
        """Record a metric (deferred to ROADMAP-030)."""
        raise NotImplementedInPhaseError("ROADMAP-030", "FileExperimentTracker.log_metric")

    def write_manifest(self, manifest: ExperimentManifest) -> None:
        """Persist run manifest (deferred to ROADMAP-030)."""
        raise NotImplementedInPhaseError("ROADMAP-030", "FileExperimentTracker.write_manifest")
