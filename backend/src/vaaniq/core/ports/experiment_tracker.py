"""Experiment tracking port (REQ-137)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from vaaniq.core.domain.entities import ExperimentManifest


class ExperimentTracker(ABC):
    """Log metrics and write reproducibility manifests.

    Serves REQ-137, REQ-138. Implementation: FileExperimentTracker (ROADMAP-030).
    """

    @abstractmethod
    def log_metric(
        self,
        name: str,
        value: float,
        *,
        dims: Mapping[str, str] | None = None,
    ) -> None:
        """Record a scalar metric.

        Args:
            name: Metric name (e.g. ``eer``).
            value: Metric value.
            dims: Optional dimensions (language, condition, ...).
        """

    @abstractmethod
    def write_manifest(self, manifest: ExperimentManifest) -> None:
        """Persist a run manifest beside experiment artefacts.

        Args:
            manifest: Reproducibility record.
        """
