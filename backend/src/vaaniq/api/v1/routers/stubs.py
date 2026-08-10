"""Stub API routers returning 501 with ROADMAP references (ROADMAP-007)."""

from __future__ import annotations

from fastapi import APIRouter

from vaaniq.core.errors import NotImplementedInPhaseError

inference_router = APIRouter(prefix="/api/v1/inference", tags=["inference"])
uploads_router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])
history_router = APIRouter(prefix="/api/v1/history", tags=["history"])
experiments_router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])
metrics_router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])
calibration_router = APIRouter(prefix="/api/v1/calibration", tags=["calibration"])
explain_router = APIRouter(prefix="/api/v1/explain", tags=["explain"])
human_study_router = APIRouter(prefix="/api/v1/human-study", tags=["human_study"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@inference_router.post("")
def infer_stub() -> None:
    """Inference stub — implemented in ROADMAP-054+."""
    raise NotImplementedInPhaseError("ROADMAP-054", "inference not implemented")


@uploads_router.post("")
def upload_stub() -> None:
    """Upload stub — implemented in ROADMAP-054 / ROADMAP-057."""
    raise NotImplementedInPhaseError("ROADMAP-054", "uploads not implemented")


@history_router.get("")
def history_stub() -> None:
    """History stub — implemented in ROADMAP-054+."""
    raise NotImplementedInPhaseError("ROADMAP-054", "history not implemented")


@experiments_router.get("")
def experiments_stub() -> None:
    """Experiments stub — implemented in ROADMAP-030+."""
    raise NotImplementedInPhaseError("ROADMAP-030", "experiments not implemented")


@metrics_router.get("")
def metrics_stub() -> None:
    """Research metrics stub — implemented in ROADMAP-036+."""
    raise NotImplementedInPhaseError("ROADMAP-036", "metrics not implemented")


@calibration_router.get("")
def calibration_stub() -> None:
    """Calibration stub — implemented in ROADMAP-043+."""
    raise NotImplementedInPhaseError("ROADMAP-043", "calibration not implemented")


@explain_router.get("")
def explain_stub() -> None:
    """Explainability stub — implemented in ROADMAP-049+."""
    raise NotImplementedInPhaseError("ROADMAP-049", "explain not implemented")


@human_study_router.get("")
def human_study_stub() -> None:
    """Human-study stub — implemented in ROADMAP-059+."""
    raise NotImplementedInPhaseError("ROADMAP-059", "human study not implemented")


@admin_router.get("")
def admin_stub() -> None:
    """Admin stub — implemented in ROADMAP-007 follow-ons / ROADMAP-062."""
    raise NotImplementedInPhaseError("ROADMAP-062", "admin not implemented")


STUB_ROUTERS = (
    inference_router,
    uploads_router,
    history_router,
    experiments_router,
    metrics_router,
    calibration_router,
    explain_router,
    human_study_router,
    admin_router,
)
