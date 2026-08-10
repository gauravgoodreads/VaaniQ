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
    ("method", "path", "roadmap_id"),
    [
        ("POST", "/api/v1/inference", "ROADMAP-054"),
        ("POST", "/api/v1/uploads", "ROADMAP-054"),
        ("GET", "/api/v1/history", "ROADMAP-054"),
        ("GET", "/api/v1/experiments", "ROADMAP-030"),
        ("GET", "/api/v1/metrics", "ROADMAP-036"),
        ("GET", "/api/v1/calibration", "ROADMAP-043"),
        ("GET", "/api/v1/explain", "ROADMAP-049"),
        ("GET", "/api/v1/human-study", "ROADMAP-059"),
        ("GET", "/api/v1/admin", "ROADMAP-062"),
    ],
)
def test_stubs_return_501_problem_json(
    client: TestClient,
    method: str,
    path: str,
    roadmap_id: str,
) -> None:
    response = client.request(method, path)
    assert response.status_code == 501
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["title"] == "NotImplementedInPhaseError"
    assert body["roadmap_id"] == roadmap_id
    assert roadmap_id in (body.get("detail") or "")
