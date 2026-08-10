"""Tests for exception hierarchy and ports (ROADMAP-003)."""

from __future__ import annotations

import inspect
from abc import ABC

import pytest

from vaaniq.core import ports
from vaaniq.core.errors import (
    NotImplementedInPhaseError,
    VaaniQError,
    ValidationError,
)
from vaaniq.core.ports import (
    AudioLoader,
    AudioValidator,
    Calibrator,
    Classifier,
    Compressor,
    DatasetSourcePort,
    EmbeddingCache,
    ExperimentTracker,
    Explainer,
    FeatureExtractor,
    HumanStudyExporter,
    ObjectStore,
    Preprocessor,
    Repository,
)

PORT_CLASSES = [
    AudioLoader,
    AudioValidator,
    Preprocessor,
    Compressor,
    FeatureExtractor,
    EmbeddingCache,
    Classifier,
    Calibrator,
    Explainer,
    DatasetSourcePort,
    Repository,
    ObjectStore,
    ExperimentTracker,
    HumanStudyExporter,
]


def test_vaaniq_error_is_root() -> None:
    """ValidationError subclasses VaaniQError."""
    err = ValidationError("bad upload")
    assert isinstance(err, VaaniQError)


def test_not_implemented_carries_roadmap_id() -> None:
    """Deferred features cite ROADMAP ids."""
    err = NotImplementedInPhaseError("ROADMAP-025", "XLS-R extract")
    assert err.roadmap_id == "ROADMAP-025"
    assert "ROADMAP-025" in str(err)


@pytest.mark.parametrize("port_cls", PORT_CLASSES)
def test_ports_are_abstract(port_cls: type) -> None:
    """Every architecture port is an ABC and cannot be instantiated."""
    assert issubclass(port_cls, ABC)
    with pytest.raises(TypeError):
        port_cls()  # type: ignore[call-arg]


@pytest.mark.parametrize("port_cls", PORT_CLASSES)
def test_port_docstring_names_req_or_roadmap(port_cls: type) -> None:
    """Port class docstrings cite REQ or ROADMAP ids."""
    doc = inspect.getdoc(port_cls)
    assert doc is not None
    assert ("REQ-" in doc) or ("ROADMAP-" in doc)


def test_ports_package_exports_match_architecture() -> None:
    """ports.__all__ lists the fourteen architecture ports."""
    assert len(ports.__all__) == 14
