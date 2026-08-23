"""Health and readiness endpoints (ROADMAP-007)."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text

from vaaniq.api.deps import get_config
from vaaniq.api.schemas import HealthResponse, ReadyResponse
from vaaniq.config.models import AppConfig
from vaaniq.persistence.session import create_db_engine

log = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe — process is up."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadyResponse)
def ready(config: Annotated[AppConfig, Depends(get_config)]) -> ReadyResponse:
    """Readiness probe — config loaded and database reachable."""
    engine = create_db_engine(config.database_url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
        status = "ready"
    except Exception:
        log.warning("readiness_db_unreachable")
        db_status = "error"
        status = "not_ready"
    finally:
        engine.dispose()
    return ReadyResponse(status=status, database=db_status)
