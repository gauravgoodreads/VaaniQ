"""Research catalogue, dataset explorer, and admin API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExperimentCompareResponse(BaseModel):
    """Experiment comparison table."""

    model_config = ConfigDict(extra="forbid")

    metric: str
    rows: list[dict[str, Any]]


class AdminStatusResponse(BaseModel):
    """Monitoring hook for deployment (ROADMAP-062)."""

    model_config = ConfigDict(extra="forbid")

    status: str
    env: str
    hardware: dict[str, str]
    git_sha: str


class DatasetSampleClip(BaseModel):
    """One explorer sample row (demo corpus)."""

    model_config = ConfigDict(extra="forbid")

    clip_id: str
    language: str
    label: str
    compression_status: str
    duration_sec: float
    has_audio: bool = False


class DatasetExplorerResponse(BaseModel):
    """Dataset explorer payload (O1 / REQ-034)."""

    model_config = ConfigDict(extra="forbid")

    total_clips: int
    total_hours: float
    counts_by_language: dict[str, int]
    hours_by_language: dict[str, float]
    counts_by_label: dict[str, int]
    hours_by_label: dict[str, float]
    languages: list[str]
    note: str
    playable_clips: int = 0
    samples: list[DatasetSampleClip] = Field(default_factory=list)
