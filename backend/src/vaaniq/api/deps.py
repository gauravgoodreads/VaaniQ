"""FastAPI dependency providers (ROADMAP-007)."""

from __future__ import annotations

from fastapi import Request

from vaaniq.api.services.ml_demo import MlApiService
from vaaniq.api.services.research import ResearchApiService
from vaaniq.config.models import AppConfig
from vaaniq.container import AppContainer, build_container


def get_config(request: Request) -> AppConfig:
    """Return the application config bound on ``app.state``."""
    config = getattr(request.app.state, "config", None)
    if not isinstance(config, AppConfig):
        msg = "application config is not configured"
        raise RuntimeError(msg)
    return config


def get_container(request: Request) -> AppContainer:
    """Return the DI container bound on ``app.state``."""
    container = getattr(request.app.state, "container", None)
    if isinstance(container, AppContainer):
        return container
    cfg = get_config(request)
    built = build_container(cfg)
    request.app.state.container = built
    return built


def get_ml_service(request: Request) -> MlApiService:
    """Return ML API service (lazy on app.state)."""
    service = getattr(request.app.state, "ml_service", None)
    if isinstance(service, MlApiService):
        return service
    service = MlApiService(get_container(request))
    request.app.state.ml_service = service
    return service


def get_research_service(request: Request) -> ResearchApiService:
    """Return research/human-study API service."""
    service = getattr(request.app.state, "research_service", None)
    if isinstance(service, ResearchApiService):
        return service
    service = ResearchApiService(get_container(request))
    request.app.state.research_service = service
    return service
