"""Composition root tests (Phase 1 step 8)."""

from __future__ import annotations

from pathlib import Path

from vaaniq.config.models import AppConfig, PathsConfig
from vaaniq.container import AppContainer, build_container
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.ports.feature_extractor import FeatureExtractor
from vaaniq.core.ports.object_store import ObjectStore
from vaaniq.storage import LocalObjectStore


def test_build_container_wires_ports(tmp_path: Path) -> None:
    config = AppConfig(
        paths=PathsConfig(
            object_store_root=tmp_path / "obj",
            embedding_cache_root=tmp_path / "emb",
        )
    )
    container = build_container(config)
    assert isinstance(container, AppContainer)
    assert container.config is config
    assert isinstance(container.feature_extractor, FeatureExtractor)
    assert isinstance(container.classifier, Classifier)
    assert isinstance(container.object_store, ObjectStore)
    assert isinstance(container.object_store, LocalObjectStore)
