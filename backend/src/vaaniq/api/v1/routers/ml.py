"""ML API routers - inference, upload, history, experiments, metrics, calibration, explain, live."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import PlainTextResponse

from vaaniq.api.deps import get_ml_service
from vaaniq.api.schemas.ml import (
    CalibrationResponse,
    ExperimentItem,
    ExperimentsResponse,
    ExplainResponse,
    HistoryResponse,
    LiveIngestResponse,
    MetricsResponse,
    PredictionResponse,
    ReportResponse,
    UploadResponse,
)
from vaaniq.api.services.ml_demo import MlApiService
from vaaniq.core.errors import ValidationError
from vaaniq.core.types import Language

inference_router = APIRouter(prefix="/api/v1/inference", tags=["inference"])
uploads_router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])
history_router = APIRouter(prefix="/api/v1/history", tags=["history"])
experiments_router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])
metrics_router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])
calibration_router = APIRouter(prefix="/api/v1/calibration", tags=["calibration"])
explain_router = APIRouter(prefix="/api/v1/explain", tags=["explain"])
live_router = APIRouter(prefix="/api/v1/live", tags=["live"])

MlServiceDep = Annotated[MlApiService, Depends(get_ml_service)]


@uploads_router.post("", response_model=UploadResponse)
async def upload_audio(
    service: MlServiceDep,
    file: Annotated[UploadFile, File()],
) -> UploadResponse:
    """Upload and validate an audio file (REQ-084, REQ-135)."""
    data = await file.read()
    content_type = file.content_type or "application/octet-stream"
    return service.upload(file.filename or "audio.wav", content_type, data)


@inference_router.post("", response_model=PredictionResponse)
async def infer(
    service: MlServiceDep,
    file: Annotated[UploadFile | None, File()] = None,
    upload_id: Annotated[str | None, Form()] = None,
    language: Annotated[str, Form()] = "hi",
    model_id: Annotated[str, Form()] = "aasist-v1",
) -> PredictionResponse:
    """Run inference from upload_id or multipart file (REQ-085-091)."""
    try:
        lang = Language(language)
    except ValueError as exc:
        raise ValidationError(f"unsupported language={language}") from exc
    if file is not None:
        data = await file.read()
        return service.infer_bytes(
            data,
            filename=file.filename or "clip.wav",
            content_type=file.content_type or "application/octet-stream",
            language=lang,
            model_id=model_id,
        )
    if upload_id:
        return service.infer_upload(upload_id, language=lang, model_id=model_id)
    raise ValidationError("provide file or upload_id")


@history_router.get("", response_model=HistoryResponse)
def history(service: MlServiceDep) -> HistoryResponse:
    """List recent predictions."""
    return HistoryResponse(items=service.history())


@experiments_router.get("", response_model=ExperimentsResponse)
def experiments(service: MlServiceDep) -> ExperimentsResponse:
    """List experiment runs."""
    items = [ExperimentItem(**row) for row in service.experiments()]
    return ExperimentsResponse(items=items)


@metrics_router.get("", response_model=MetricsResponse)
def metrics(service: MlServiceDep) -> MetricsResponse:
    """Research metrics snapshot (RQ1-RQ3 tables)."""
    snap = service.metrics_snapshot()
    return MetricsResponse(
        metrics=snap["metrics"],  # type: ignore[arg-type]
        matrices=snap["matrices"],  # type: ignore[arg-type]
        slices=snap["slices"],  # type: ignore[arg-type]
    )


@calibration_router.get("", response_model=CalibrationResponse)
def calibration(service: MlServiceDep) -> CalibrationResponse:
    """Calibration ECE / reliability snapshot (RQ4)."""
    return service.calibration_snapshot()


@metrics_router.get("/pipeline")
def pipeline_status(service: MlServiceDep) -> dict[str, object]:
    """Trained pipeline status (weights, calibration, corpus training report)."""
    return service.pipeline_status()


@explain_router.get("", response_model=ExplainResponse)
def explain(
    service: MlServiceDep,
    prediction_id: str | None = None,
) -> ExplainResponse:
    """Explainability artefacts for a prediction."""
    return service.explain_last(prediction_id)


@live_router.post("/session")
def live_session(service: MlServiceDep) -> dict[str, str]:
    """Create a live MediaRecorder session (REQ-096)."""
    return {"session_id": service.live_start()}


@live_router.post("/ingest", response_model=LiveIngestResponse)
async def live_ingest(
    service: MlServiceDep,
    session_id: Annotated[str, Form()],
    chunk: Annotated[UploadFile, File()],
) -> LiveIngestResponse:
    """Ingest a PCM chunk for sliding-window inference."""
    data = await chunk.read()
    preds = service.live_ingest(session_id, data)
    return LiveIngestResponse(session_id=session_id, predictions=preds)


@experiments_router.get("/report", response_model=ReportResponse)
def experiment_report(
    service: MlServiceDep,
    experiment_id: str = "demo",
) -> ReportResponse:
    """Downloadable evaluation report markdown."""
    md = service.write_report(experiment_id)
    return ReportResponse(report_markdown=md, experiment_id=experiment_id)


@experiments_router.get("/report.md")
def experiment_report_md(
    service: MlServiceDep,
    experiment_id: str = "demo",
) -> PlainTextResponse:
    """Raw markdown report download."""
    md = service.write_report(experiment_id)
    return PlainTextResponse(md, media_type="text/markdown")


ML_ROUTERS = (
    inference_router,
    uploads_router,
    history_router,
    experiments_router,
    metrics_router,
    calibration_router,
    explain_router,
    live_router,
)
