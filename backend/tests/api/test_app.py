"""API tests for the FastAPI application factory (ROADMAP-007)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from vaaniq.api import create_app
from vaaniq.config.models import ApiConfig, AppConfig


@pytest.fixture
def config(tmp_path: Path) -> AppConfig:
    """Isolated SQLite-backed config for API tests."""
    db_path = tmp_path / "api_test.db"
    return AppConfig(
        env="local",
        database_url=f"sqlite:///{db_path.as_posix()}",
        api=ApiConfig(
            cors_origins=[
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        ),
    )


@pytest.fixture
def client(config: AppConfig) -> TestClient:
    """TestClient for a freshly created app."""
    return TestClient(create_app(config))


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_health_ready_ok(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


def test_version(client: TestClient, config: AppConfig) -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == config.project.name
    assert body["api_version"] == "v1"
    assert body["env"] == "local"
    assert "version" in body


def test_openapi_docs_available(client: TestClient) -> None:
    docs = client.get("/docs")
    assert docs.status_code == 200
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    schema = openapi.json()
    assert schema["info"]["title"] == "VaaniQ"
    paths = schema["paths"]
    assert "/health" in paths
    assert "/api/v1/version" in paths
    assert "/api/v1/human-study/register" in paths
    assert "/api/v1/datasets/explorer" in paths


def test_cors_allows_configured_origin(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/history"),
        ("GET", "/api/v1/experiments"),
        ("GET", "/api/v1/metrics"),
        ("GET", "/api/v1/calibration"),
        ("GET", "/api/v1/explain"),
        ("GET", "/api/v1/human-study/report"),
        ("GET", "/api/v1/admin/status"),
        ("GET", "/api/v1/datasets/explorer"),
        ("GET", "/api/v1/experiments/compare"),
    ],
)
def test_research_and_ml_routes_live(client: TestClient, method: str, path: str) -> None:
    """Phase-4 routers return 2xx rather than 501 stubs."""
    response = client.request(method, path)
    assert response.status_code == 200, path


def test_human_study_register(client: TestClient) -> None:
    """Volunteer registration returns an anonymous id and balanced clips."""
    response = client.post(
        "/api/v1/human-study/register",
        json={"fluency_self_report": "hi+mr"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["participant_id"]
    assert body["clip_ids"]


def test_openapi_hidden_in_prod(tmp_path: Path) -> None:
    """Production profile must not expose Swagger (REQ-136)."""
    db_path = tmp_path / "prod.db"
    cfg = AppConfig(
        env="prod",
        database_url=f"sqlite:///{db_path.as_posix()}",
        api=ApiConfig(cors_origins=["http://localhost:5173"]),
    )
    prod_client = TestClient(create_app(cfg))
    assert prod_client.get("/docs").status_code == 404
    assert prod_client.get("/openapi.json").status_code == 404


def test_inference_rejects_unsupported_language(client: TestClient) -> None:
    response = client.post("/api/v1/inference", data={"language": "xx", "model_id": "aasist-v1"})
    assert response.status_code == 400


def test_upload_rejects_oversized_payload(tmp_path: Path) -> None:
    cfg = AppConfig(
        env="local",
        database_url=f"sqlite:///{(tmp_path / 'oversize.db').as_posix()}",
        api=ApiConfig(max_upload_bytes=64, cors_origins=["http://localhost:5173"]),
    )
    oversized = TestClient(create_app(cfg))
    payload = b"RIFF" + b"x" * 200
    response = oversized.post(
        "/api/v1/uploads",
        files={"file": ("clip.wav", payload, "audio/wav")},
    )
    assert response.status_code == 400


def test_upload_ignores_path_traversal_filename(client: TestClient, tmp_path: Path) -> None:
    from vaaniq.api.services.ml_demo import write_sine_wav

    wav = tmp_path / "ok.wav"
    write_sine_wav(wav, seconds=0.6)
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("../../../etc/passwd.wav", wav.read_bytes(), "audio/wav")},
    )
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]
    infer = client.post(
        "/api/v1/inference",
        data={"upload_id": upload_id, "language": "hi", "model_id": "aasist-v1"},
    )
    assert infer.status_code == 200


def test_inference_rejects_long_audio(tmp_path: Path) -> None:
    from vaaniq.api.services.ml_demo import write_sine_wav

    cfg = AppConfig(
        env="local",
        database_url=f"sqlite:///{(tmp_path / 'dur.db').as_posix()}",
        api=ApiConfig(max_audio_duration_sec=1, cors_origins=["http://localhost:5173"]),
    )
    timed = TestClient(create_app(cfg))
    wav = tmp_path / "long.wav"
    write_sine_wav(wav, seconds=2.0)
    response = timed.post(
        "/api/v1/inference",
        files={"file": ("long.wav", wav.read_bytes(), "audio/wav")},
        data={"language": "hi", "model_id": "aasist-v1"},
    )
    assert response.status_code == 400
