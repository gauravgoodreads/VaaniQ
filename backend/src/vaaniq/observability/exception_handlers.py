"""Map domain errors to RFC 7807 problem responses (ROADMAP-005)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from vaaniq.core.errors import (
    AudioDecodeError,
    CalibrationError,
    ConfigurationError,
    DatasetError,
    ModelNotReadyError,
    NotImplementedInPhaseError,
    PersistenceError,
    VaaniQError,
    ValidationError,
)
from vaaniq.observability.context import get_request_id
from vaaniq.observability.logging import get_logger
from vaaniq.observability.problems import ProblemDetails

_LOG = get_logger(__name__)

_PROBLEM_MEDIA_TYPE = "application/problem+json"

_STATUS_BY_TYPE: dict[type[BaseException], int] = {
    ValidationError: 400,
    AudioDecodeError: 400,
    DatasetError: 502,
    ConfigurationError: 500,
    PersistenceError: 500,
    CalibrationError: 500,
    ModelNotReadyError: 503,
    NotImplementedInPhaseError: 501,
    VaaniQError: 500,
}

_ExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]


def _status_for(exc: BaseException) -> int:
    """Resolve HTTP status for ``exc``."""
    for exc_type, status in _STATUS_BY_TYPE.items():
        if isinstance(exc, exc_type):
            return status
    return 500


def _title_for(exc: BaseException) -> str:
    """Human-readable title from the exception class name."""
    return type(exc).__name__


def problem_from_exception(exc: BaseException, *, instance: str | None = None) -> ProblemDetails:
    """Build a ProblemDetails document from an exception.

    Args:
        exc: Raised exception.
        instance: Optional request path for the ``instance`` field.
    """
    status = _status_for(exc)
    detail = str(exc) if str(exc) else None
    extras: dict[str, str] = {}
    if isinstance(exc, NotImplementedInPhaseError):
        extras["roadmap_id"] = exc.roadmap_id
    return ProblemDetails(
        type=f"https://vaaniq.local/problems/{type(exc).__name__}",
        title=_title_for(exc),
        status=status,
        detail=detail,
        instance=instance,
        request_id=get_request_id(),
        **extras,
    )


async def vaaniq_error_handler(request: Request, exc: VaaniQError) -> JSONResponse:
    """Handle ``VaaniQError`` subclasses as problem+json."""
    problem = problem_from_exception(exc, instance=str(request.url.path))
    _LOG.warning(
        "request_failed",
        error_type=type(exc).__name__,
        status=problem.status,
        detail=problem.detail,
    )
    return JSONResponse(
        status_code=problem.status,
        content=problem.to_response_dict(),
        media_type=_PROBLEM_MEDIA_TYPE,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without leaking internals."""
    _LOG.exception("unhandled_error", path=str(request.url.path))
    problem = ProblemDetails(
        type="https://vaaniq.local/problems/InternalServerError",
        title="Internal Server Error",
        status=500,
        detail="An unexpected error occurred.",
        instance=str(request.url.path),
        request_id=get_request_id(),
    )
    return JSONResponse(
        status_code=500,
        content=problem.to_response_dict(),
        media_type=_PROBLEM_MEDIA_TYPE,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach VaaniQ exception handlers to ``app``.

    Args:
        app: FastAPI application instance.
    """
    # Starlette types handlers as Exception; our handlers narrow to VaaniQError.
    app.add_exception_handler(
        VaaniQError,
        cast(_ExceptionHandler, vaaniq_error_handler),
    )
    app.add_exception_handler(
        Exception,
        cast(_ExceptionHandler, unhandled_error_handler),
    )
