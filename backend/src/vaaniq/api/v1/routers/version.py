"""Version endpoint (ROADMAP-007 / REQ-001)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from vaaniq import __version__
from vaaniq.api.deps import get_config
from vaaniq.api.schemas import VersionResponse
from vaaniq.config.models import AppConfig

router = APIRouter(prefix="/api/v1", tags=["version"])


@router.get("/version", response_model=VersionResponse)
def version(config: Annotated[AppConfig, Depends(get_config)]) -> VersionResponse:
    """Return package and API version metadata."""
    return VersionResponse(
        name=config.project.name,
        version=__version__,
        api_version="v1",
        env=config.env,
    )
