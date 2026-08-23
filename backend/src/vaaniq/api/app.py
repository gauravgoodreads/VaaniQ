"""FastAPI application factory (ROADMAP-007)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vaaniq import __version__
from vaaniq.api.v1.routers import health, version
from vaaniq.api.v1.routers.ml import ML_ROUTERS
from vaaniq.api.v1.routers.research import RESEARCH_ROUTERS
from vaaniq.config.loader import load_config
from vaaniq.config.models import AppConfig
from vaaniq.container import build_container
from vaaniq.observability import (
    RequestIdMiddleware,
    configure_logging,
    register_exception_handlers,
)


def create_app(config: AppConfig | None = None) -> FastAPI:
    """Build and wire the VaaniQ FastAPI application.

    Args:
        config: Optional pre-loaded config. When omitted, layered defaults are used.

    Returns:
        Configured FastAPI app with health, version, ML, and research routers.
    """
    cfg = config if config is not None else load_config()
    configure_logging(log_level=cfg.log_level, json_logs=True)

    app = FastAPI(
        title=cfg.project.name,
        version=__version__,
        description=(
            "Cross-lingual, compression-robust AI-voice detection for Hindi, "
            "Marathi, and Tamil with calibrated reliability."
        ),
        docs_url="/docs" if cfg.env != "prod" else None,
        redoc_url="/redoc" if cfg.env != "prod" else None,
        openapi_url="/openapi.json" if cfg.env != "prod" else None,
    )
    app.state.config = cfg
    app.state.container = build_container(cfg)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins_for_env(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(version.router)
    for router in ML_ROUTERS:
        app.include_router(router)
    for router in RESEARCH_ROUTERS:
        app.include_router(router)

    return app
