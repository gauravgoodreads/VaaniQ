"""Request-scoped context for structured logging (ROADMAP-005)."""

from __future__ import annotations

from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Return the current request id, if any."""
    return request_id_ctx.get()


def bind_request_id(request_id: str) -> None:
    """Bind ``request_id`` into the context var for the current task."""
    request_id_ctx.set(request_id)
