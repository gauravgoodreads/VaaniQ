"""structlog JSON logging setup (ROADMAP-005).

No ``print()`` in library code; use structured kwargs only (vaaniq-core.mdc).
"""

from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any, cast

import structlog

from vaaniq.observability.context import get_request_id


def _add_request_id(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Inject request_id from contextvars when present."""
    request_id = get_request_id()
    if request_id is not None:
        event_dict.setdefault("request_id", request_id)
    return event_dict


def configure_logging(*, log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure stdlib logging + structlog.

    Args:
        log_level: Root log level name (e.g. ``INFO``).
        json_logs: When True, emit JSON lines (default for all envs).
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", level=level, force=True)

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        _add_request_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger.

    Args:
        name: Optional logger name; defaults to ``vaaniq``.
    """
    return cast(
        structlog.stdlib.BoundLogger,
        structlog.get_logger(name or "vaaniq"),
    )
