"""Experiment compare, dataset explorer, and admin monitoring routers."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from vaaniq.api.deps import get_config, get_research_service
from vaaniq.api.schemas.research import (
    AdminStatusResponse,
    DatasetExplorerResponse,
    ExperimentCompareResponse,
)
from vaaniq.api.services.research import ResearchApiService
from vaaniq.config.models import AppConfig

admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
experiments_extra_router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])

ResearchDep = Annotated[ResearchApiService, Depends(get_research_service)]


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
    service.reload_pool()
    payload = service.dataset_explorer()
    return DatasetExplorerResponse.model_validate(payload)


@datasets_router.get("/clips/{clip_id}/audio")
def dataset_clip_audio(clip_id: str, service: ResearchDep) -> FileResponse:
    """Stream a corpus clip for dataset-explorer playback."""
    return service.clip_audio(clip_id)


@datasets_router.get("/clips/{clip_id}")
def dataset_clip_meta(clip_id: str, service: ResearchDep) -> dict[str, object]:
    """Clip metadata for the dataset explorer."""
    return service.clip_meta(clip_id)


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
    admin_router,
    experiments_extra_router,
    datasets_router,
)
