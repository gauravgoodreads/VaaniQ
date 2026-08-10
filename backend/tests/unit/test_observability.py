"""Tests for observability helpers (ROADMAP-005)."""

from __future__ import annotations

import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from vaaniq.core.errors import NotImplementedInPhaseError, ValidationError
from vaaniq.observability import (
    ProblemDetails,
    RequestIdMiddleware,
    configure_logging,
    get_logger,
    get_request_id,
    register_exception_handlers,
)
from vaaniq.observability.context import bind_request_id, request_id_ctx
from vaaniq.observability.exception_handlers import problem_from_exception


def _mini_app() -> FastAPI:
    """Build a tiny FastAPI app with observability wired."""
    configure_logging(log_level="INFO", json_logs=True)
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    @app.get("/ok")
    def ok() -> dict[str, str]:
        rid = get_request_id()
        return {"request_id": rid or ""}

    @app.get("/boom-validation")
    def boom_validation() -> None:
        raise ValidationError("bad clip")

    @app.get("/boom-roadmap")
    def boom_roadmap() -> None:
        raise NotImplementedInPhaseError("ROADMAP-025", "XLS-R not ready")

    @app.get("/boom-unhandled")
    def boom_unhandled() -> None:
        raise RuntimeError("secret internals")

    return app


def test_configure_logging_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON renderer writes a parseable log line."""
    configure_logging(log_level="INFO", json_logs=True)
    log = get_logger("vaaniq.test")
    log.info("hello_event", clip_id="c1")
    # stdlib handler may write to stderr
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "hello_event" in combined
    # Find a JSON object line
    lines = [ln for ln in combined.splitlines() if ln.strip().startswith("{")]
    assert lines
    payload = json.loads(lines[-1])
    assert payload["event"] == "hello_event"
    assert payload["clip_id"] == "c1"


def test_request_id_generated_and_echoed() -> None:
    """Middleware assigns and echoes X-Request-ID."""
    client = TestClient(_mini_app())
    response = client.get("/ok")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_request_id_inbound_preserved() -> None:
    """Inbound X-Request-ID is reused."""
    client = TestClient(_mini_app())
    response = client.get("/ok", headers={"X-Request-ID": "req-fixed-1"})
    assert response.headers["X-Request-ID"] == "req-fixed-1"
    assert response.json()["request_id"] == "req-fixed-1"


def test_validation_error_is_problem_json() -> None:
    """VaaniQ validation errors return problem+json 400."""
    client = TestClient(_mini_app(), raise_server_exceptions=False)
    response = client.get("/boom-validation")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["title"] == "ValidationError"
    assert body["detail"] == "bad clip"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_not_implemented_includes_roadmap_id() -> None:
    """501 responses include roadmap_id extension."""
    client = TestClient(_mini_app(), raise_server_exceptions=False)
    response = client.get("/boom-roadmap")
    assert response.status_code == 501
    body = response.json()
    assert body["roadmap_id"] == "ROADMAP-025"


def test_unhandled_hides_internals() -> None:
    """Unhandled errors do not leak exception text."""
    client = TestClient(_mini_app(), raise_server_exceptions=False)
    response = client.get("/boom-unhandled")
    assert response.status_code == 500
    body = response.json()
    assert "secret internals" not in json.dumps(body)
    assert body["title"] == "Internal Server Error"


def test_problem_details_model() -> None:
    """ProblemDetails serialises RFC 7807 fields."""
    problem = ProblemDetails(title="t", status=400, detail="d", request_id="r1")
    data = problem.to_response_dict()
    assert data["status"] == 400
    assert data["request_id"] == "r1"


def test_problem_from_exception_binds_context() -> None:
    """problem_from_exception includes bound request id."""
    token = request_id_ctx.set("ctx-1")
    try:
        bind_request_id("ctx-1")
        problem = problem_from_exception(ValidationError("x"), instance="/x")
        assert problem.request_id == "ctx-1"
        assert problem.instance == "/x"
    finally:
        request_id_ctx.reset(token)


def test_logging_level_fallback() -> None:
    """Unknown level names fall back safely via getattr default."""
    configure_logging(log_level="NOT_A_LEVEL", json_logs=True)
    assert logging.getLogger().level == logging.INFO


def test_console_renderer_path() -> None:
    """Non-JSON mode configures without error."""
    configure_logging(log_level="INFO", json_logs=False)
    get_logger("vaaniq.console").info("console_event")


def test_status_for_unknown_exception() -> None:
    """Unmapped exceptions default to HTTP 500."""
    problem = problem_from_exception(RuntimeError("x"))
    assert problem.status == 500
