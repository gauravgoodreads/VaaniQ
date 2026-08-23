"""Versioned API routers."""

from __future__ import annotations

from vaaniq.api.v1.routers import health, version
from vaaniq.api.v1.routers.ml import ML_ROUTERS
from vaaniq.api.v1.routers.research import RESEARCH_ROUTERS
from vaaniq.api.v1.routers.stubs import STUB_ROUTERS

__all__ = ["ML_ROUTERS", "RESEARCH_ROUTERS", "STUB_ROUTERS", "health", "version"]
