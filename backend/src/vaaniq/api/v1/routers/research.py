"""Human-study, experiment compare, and admin monitoring routers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from vaaniq.api.deps import get_config, get_research_service
from vaaniq.api.schemas.research import (
    AdminStatusResponse,
    DatasetExplorerResponse,
    ExperimentCompareResponse,
    HumanResponseIn,
    HumanStudyReportResponse,
    ParticipantCreate,
    ParticipantResponse,
)
from vaaniq.api.services.research import ResearchApiService
from vaaniq.config.models import AppConfig
from vaaniq.core.types import ExportFormat

human_study_router = APIRouter(prefix="/api/v1/human-study", tags=["human_study"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
experiments_extra_router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])

ResearchDep = Annotated[ResearchApiService, Depends(get_research_service)]


@human_study_router.post("/register", response_model=ParticipantResponse)
def register(body: ParticipantCreate, service: ResearchDep) -> ParticipantResponse:
    """Register an anonymous volunteer and assign balanced clips (RQ5)."""
    session = service.register(body)
    return ParticipantResponse(
        participant_id=session.participant_id,
        fluency_self_report=session.fluency_self_report,
        clip_ids=session.clip_ids,
    )


@human_study_router.post("/response")
def submit_response(body: HumanResponseIn, service: ResearchDep) -> dict[str, str]:
    """Record a timed real/fake judgement with 1-5 confidence."""
    return service.record(body)


@human_study_router.get("/export")
def export_responses(service: ResearchDep) -> dict[str, str]:
    """Write anonymised CSV under the object-store root."""
    dest = Path("./research/human_study/export.csv")
    path = service.export(dest, ExportFormat.CSV)
    return {"path": str(path)}


@human_study_router.get("/report", response_model=HumanStudyReportResponse)
def human_report(service: ResearchDep) -> HumanStudyReportResponse:
    """Human vs model accuracy/calibration comparison (RQ5)."""
    payload = service.comparison_report()
    stats = payload["stats"]
    n_raw = payload["n_responses"]
    if not isinstance(stats, dict):
        stats = {}
    n_responses = int(n_raw) if isinstance(n_raw, int | float | str) else 0
    return HumanStudyReportResponse(stats=stats, n_responses=n_responses)


@experiments_extra_router.get("/compare", response_model=ExperimentCompareResponse)
def compare_experiments(
    service: ResearchDep,
    metric: str = "eer",
) -> ExperimentCompareResponse:
    """Compare stored experiments on a named metric."""
    return ExperimentCompareResponse(metric=metric, rows=service.compare_experiments(metric))


@experiments_extra_router.get("/search")
def search_experiments(
    service: ResearchDep,
    language: str | None = None,
    model_version: str | None = None,
    rq_id: str | None = None,
) -> dict[str, object]:
    """Search the research catalogue."""
    return {
        "items": service.search_experiments(
            language=language, model_version=model_version, rq_id=rq_id
        )
    }


datasets_router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


@datasets_router.get("/explorer", response_model=DatasetExplorerResponse)
def dataset_explorer(service: ResearchDep) -> DatasetExplorerResponse:
    """Language x label hours for the active clip pool (O1)."""
    payload = service.dataset_explorer()
    return DatasetExplorerResponse.model_validate(payload)


@admin_router.get("/status", response_model=AdminStatusResponse)
def admin_status(
    service: ResearchDep,
    config: Annotated[AppConfig, Depends(get_config)],
) -> AdminStatusResponse:
    """Health/monitoring hook for compose and Spaces."""
    return AdminStatusResponse(
        status="ok",
        env=config.env,
        hardware=service.hardware(),
        git_sha=service.git_sha(),
    )


RESEARCH_ROUTERS = (
    human_study_router,
    admin_router,
    experiments_extra_router,
    datasets_router,
)
