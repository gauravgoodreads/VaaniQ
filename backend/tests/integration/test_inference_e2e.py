"""End-to-end API slice: upload → infer → history → research (no network/GPU)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from vaaniq.api import create_app
from vaaniq.api.services.ml_demo import write_sine_wav
from vaaniq.config.models import ApiConfig, AppConfig, PathsConfig


def _client(tmp_path: Path) -> TestClient:
    """Build an isolated app with temp DB and object store."""
    cfg = AppConfig(
        env="local",
        database_url=f"sqlite:///{(tmp_path / 'e2e.db').as_posix()}",
        api=ApiConfig(cors_origins=["http://localhost:5173"]),
        paths=PathsConfig(
            object_store_root=tmp_path / "store",
            embedding_cache_root=tmp_path / "emb",
        ),
    )
    return TestClient(create_app(cfg))


def test_upload_infer_history_and_research_surface(tmp_path: Path) -> None:
    """Vertical slice covering O7 demo plus research GETs."""
    client = _client(tmp_path)
    wav = tmp_path / "clip.wav"
    write_sine_wav(wav, seconds=0.6)

    uploaded = client.post(
        "/api/v1/uploads",
        files={"file": ("clip.wav", wav.read_bytes(), "audio/wav")},
    )
    assert uploaded.status_code == 200, uploaded.text
    upload_id = uploaded.json()["upload_id"]

    inferred = client.post(
        "/api/v1/inference",
        data={"upload_id": upload_id, "language": "hi", "model_id": "aasist-v1"},
    )
    assert inferred.status_code == 200, inferred.text
    body = inferred.json()
    assert body["label"] in {"real", "fake"}
    assert 0.0 <= float(body["confidence"]) <= 1.0
    assert body["reliability"]
    assert body["language"] == "hi"

    history = client.get("/api/v1/history")
    assert history.status_code == 200
    items = history.json()["items"]
    assert items
    assert items[0]["prediction_id"] == body["prediction_id"]

    for path in (
        "/health",
        "/health/ready",
        "/api/v1/version",
        "/api/v1/metrics",
        "/api/v1/calibration",
        "/api/v1/explain",
        "/api/v1/experiments",
        "/api/v1/experiments/compare",
        "/api/v1/datasets/explorer",
        "/api/v1/human-study/report",
        "/api/v1/admin/status",
    ):
        response = client.get(path)
        assert response.status_code == 200, path

    registered = client.post(
        "/api/v1/human-study/register",
        json={"fluency_self_report": "hi"},
    )
    assert registered.status_code == 200
    assert registered.json()["clip_ids"]
