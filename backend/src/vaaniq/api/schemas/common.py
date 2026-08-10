"""Shared API response schemas (ROADMAP-007)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Liveness payload for ``/health``."""

    model_config = ConfigDict(extra="forbid")

    status: str = "ok"


class ReadyResponse(BaseModel):
    """Readiness payload for ``/health/ready``."""

    model_config = ConfigDict(extra="forbid")

    status: str
    database: str


class VersionResponse(BaseModel):
    """Build/version payload for ``/api/v1/version``."""

    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    api_version: str = Field(default="v1")
    env: str
