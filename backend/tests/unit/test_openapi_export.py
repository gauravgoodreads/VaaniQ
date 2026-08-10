"""Drift check for OpenAPI export vs committed frontend artefact (Phase 1 step 11)."""

from __future__ import annotations

import json
from pathlib import Path

from vaaniq.api.app import create_app


def _repo_root() -> Path:
    """backend/tests/unit -> repo root."""
    return Path(__file__).resolve().parents[3]


def test_openapi_export_contains_health_and_version() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    assert "/health" in paths
    assert "/api/v1/version" in paths
    components = schema["components"]["schemas"]
    assert "HealthResponse" in components
    assert "VersionResponse" in components


def test_committed_openapi_json_matches_app() -> None:
    """Committed openapi.json must match create_app().openapi() (CI drift gate)."""
    committed = _repo_root() / "frontend" / "src" / "api" / "generated" / "openapi.json"
    assert committed.is_file(), "run scripts/gen_api_types.sh to create openapi.json"
    live = create_app().openapi()
    disk = json.loads(committed.read_text(encoding="utf-8"))
    assert json.dumps(disk, sort_keys=True) == json.dumps(live, sort_keys=True)
