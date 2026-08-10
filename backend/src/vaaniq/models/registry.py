"""Model registry stub (ROADMAP-035)."""

from __future__ import annotations

from collections.abc import Mapping

from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.ports.classifier import Classifier


class ModelRegistry:
    """Resolve trained classifiers by registry id.

    TODO(ROADMAP-035): load ``models`` table / manifest entries into Classifier instances.
    """

    def get(self, model_id: str) -> Classifier:
        """Return a classifier for ``model_id`` (deferred to ROADMAP-035)."""
        raise NotImplementedInPhaseError("ROADMAP-035", f"ModelRegistry.get({model_id})")

    def list_ids(self) -> Mapping[str, str]:
        """Return model_id → description map (deferred to ROADMAP-035)."""
        raise NotImplementedInPhaseError("ROADMAP-035", "ModelRegistry.list_ids")
