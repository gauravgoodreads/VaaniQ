"""FastAPI dependency providers (ROADMAP-007)."""

from __future__ import annotations

from fastapi import Request

from vaaniq.config.models import AppConfig


def get_config(request: Request) -> AppConfig:
    """Return the application config bound on ``app.state``."""
    config = getattr(request.app.state, "config", None)
    if not isinstance(config, AppConfig):
        msg = "application config is not configured"
        raise RuntimeError(msg)
    return config
