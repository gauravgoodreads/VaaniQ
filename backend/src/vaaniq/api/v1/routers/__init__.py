"""Versioned API routers."""

from __future__ import annotations

from vaaniq.api.v1.routers import health, version
from vaaniq.api.v1.routers.stubs import STUB_ROUTERS

__all__ = ["STUB_ROUTERS", "health", "version"]
