"""Unit tests for local object store."""

from __future__ import annotations

from pathlib import Path

import pytest

from vaaniq.core.errors import PersistenceError, ValidationError
from vaaniq.storage.local import LocalObjectStore


def test_local_object_store_roundtrip(tmp_path: Path) -> None:
    store = LocalObjectStore(tmp_path)
    uri = store.put("clips/a.bin", b"hello", content_type="application/octet-stream")
    assert Path(uri).is_file()
    assert store.get("clips/a.bin") == b"hello"
    assert store.uri_for("clips/a.bin")


def test_local_object_store_rejects_traversal(tmp_path: Path) -> None:
    store = LocalObjectStore(tmp_path)
    with pytest.raises(ValidationError):
        store.put("../escape.bin", b"x")


def test_local_object_store_missing(tmp_path: Path) -> None:
    store = LocalObjectStore(tmp_path)
    with pytest.raises(PersistenceError):
        store.get("missing.bin")
