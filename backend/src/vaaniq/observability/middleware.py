"""HTTP middleware for request correlation ids (ROADMAP-005)."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from vaaniq.observability.context import bind_request_id, request_id_ctx
from vaaniq.observability.logging import get_logger

_LOG = get_logger(__name__)
_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request has an ``X-Request-ID`` and log context.

    Accepts an inbound header when present; otherwise generates a UUIDv4.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process ``request``, binding and echoing the request id."""
        inbound = request.headers.get(_HEADER)
        request_id = inbound.strip() if inbound and inbound.strip() else str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        bind_request_id(request_id)
        try:
            _LOG.info(
                "request_started",
                method=request.method,
                path=request.url.path,
            )
            response = await call_next(request)
            response.headers[_HEADER] = request_id
            _LOG.info(
                "request_finished",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
            return response
        finally:
            request_id_ctx.reset(token)
