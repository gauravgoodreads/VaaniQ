"""ML inference / research API schemas (ROADMAP-054+)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PredictionResponse(BaseModel):
    """Inference verdict payload (REQ-087-091)."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: str
    label: str
    confidence: float
    reliability: str
    language: str
    compression_status: str
    probabilities: dict[str, float]
    waveform: list[float] = Field(default_factory=list)
    spectrogram: list[list[float]] = Field(default_factory=list)


class UploadResponse(BaseModel):
    """Upload acknowledgement."""

    model_config = ConfigDict(extra="forbid")

    upload_id: str
    filename: str
    size_bytes: int
    content_type: str


class HistoryItem(BaseModel):
    """History row."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: str
    label: str
    confidence: float
    reliability: str
    language: str
    created_at: str


class HistoryResponse(BaseModel):
    """History list."""

    model_config = ConfigDict(extra="forbid")

    items: list[HistoryItem]


class ExperimentItem(BaseModel):
    """Experiment summary."""

    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    path: str


class ExperimentsResponse(BaseModel):
    """Experiment list."""

    model_config = ConfigDict(extra="forbid")

    items: list[ExperimentItem]


class MetricsResponse(BaseModel):
    """Research metrics snapshot."""

    model_config = ConfigDict(extra="forbid")

    metrics: dict[str, Any]
    matrices: dict[str, Any]
    slices: dict[str, Any]


class CalibrationResponse(BaseModel):
    """Calibration artefacts summary."""

    model_config = ConfigDict(extra="forbid")

    ece: float
    brier: float
    reliability_diagram: list[dict[str, float]]
    coverage_curve: list[dict[str, float]]
    temperatures: dict[str, float]


class ExplainResponse(BaseModel):
    """Explainability artefacts."""

    model_config = ConfigDict(extra="forbid")

    artefacts: list[dict[str, str]]


class LiveIngestResponse(BaseModel):
    """Live streaming window predictions."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    predictions: list[PredictionResponse]


class ReportResponse(BaseModel):
    """Downloadable report pointer."""

    model_config = ConfigDict(extra="forbid")

    report_markdown: str
    experiment_id: str
