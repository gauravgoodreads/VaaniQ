"""SQLAlchemy ORM models (ROADMAP-006).

PostgreSQL-compatible types only (Uuid, String, Integer, Float, DateTime, JSON).
Table set matches SYSTEM_ARCHITECTURE §8 ER diagram.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from vaaniq.persistence.base import Base


def _uuid() -> uuid.UUID:
    """Generate a new UUID4 primary key."""
    return uuid.uuid4()


class UserRow(Base):
    """Application user row (``users``)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="researcher")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    uploads: Mapped[list[UploadRow]] = relationship(back_populates="user")


class UploadRow(Base):
    """Uploaded or recorded audio clip metadata (``uploads``)."""

    __tablename__ = "uploads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    language: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    compression_status: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[UserRow | None] = relationship(back_populates="uploads")
    predictions: Mapped[list[PredictionRow]] = relationship(back_populates="upload")


class PredictionRow(Base):
    """Inference result for an upload (``predictions``)."""

    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    upload_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reliability: Mapped[str] = mapped_column(String(32), nullable=False)
    extras: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    upload: Mapped[UploadRow] = relationship(back_populates="predictions")


class ExperimentRow(Base):
    """Training or evaluation experiment run (``experiments``)."""

    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    git_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    metrics: Mapped[list[ExperimentMetricRow]] = relationship(back_populates="experiment")
    models: Mapped[list[RegisteredModelRow]] = relationship(back_populates="experiment")


class ExperimentMetricRow(Base):
    """Scalar metric logged for an experiment (``experiment_metrics``)."""

    __tablename__ = "experiment_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    dims: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    experiment: Mapped[ExperimentRow] = relationship(back_populates="metrics")


class RegisteredModelRow(Base):
    """Registered model artefact (``models``)."""

    __tablename__ = "models"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    experiment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    card: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    experiment: Mapped[ExperimentRow | None] = relationship(back_populates="models")
    calibration_runs: Mapped[list[CalibrationRunRow]] = relationship(back_populates="model")


class CalibrationRunRow(Base):
    """Temperature-scaling / calibration fit record (``calibration_runs``)."""

    __tablename__ = "calibration_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    temperatures: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    ece_pre: Mapped[float] = mapped_column(Float, nullable=False)
    ece_post: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    model: Mapped[RegisteredModelRow] = relationship(back_populates="calibration_runs")


class HumanStudyParticipantRow(Base):
    """Anonymised human-study participant (``human_study_participants``)."""

    __tablename__ = "human_study_participants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    fluency_self_report: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    responses: Mapped[list[HumanStudyResponseRow]] = relationship(back_populates="participant")


class HumanStudyResponseRow(Base):
    """Single forced-choice response (``human_study_responses``)."""

    __tablename__ = "human_study_responses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    participant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("human_study_participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clip_id: Mapped[str] = mapped_column(String(256), nullable=False)
    choice: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_1_5: Mapped[int] = mapped_column(Integer, nullable=False)
    response_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    compression_status: Mapped[str | None] = mapped_column(String(64), nullable=True)

    participant: Mapped[HumanStudyParticipantRow] = relationship(back_populates="responses")


class DatasetCatalogRow(Base):
    """Registered corpus / dataset catalog entry (``datasets``).

    Serves ROADMAP-011 / REQ-101-106.
    """

    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    gated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    licence_note: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    config_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    clips: Mapped[list[AudioClipRow]] = relationship(back_populates="dataset")


class AudioClipRow(Base):
    """Persisted clip metadata aligned with ``ClipMetadata`` (``audio_clips``).

    Optional enrichment columns: ``# ASSUMPTION: OQ-036``.
    Serves ROADMAP-011 / ROADMAP-012 / REQ-131-133.
    """

    __tablename__ = "audio_clips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    clip_id: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(16), nullable=False)
    compression_status: Mapped[str] = mapped_column(String(64), nullable=False)
    sample_rate_hz: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    split: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    dataset_source: Mapped[str] = mapped_column(String(512), nullable=False)
    speaker_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    attack_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    generation_model: Mapped[str | None] = mapped_column(String(256), nullable=True)
    pair_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    consent_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # ASSUMPTION: OQ-036
    gender: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speaker_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emotion: Mapped[str | None] = mapped_column(String(64), nullable=True)
    recording_medium: Mapped[str | None] = mapped_column(String(128), nullable=True)
    quality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    dataset: Mapped[DatasetCatalogRow | None] = relationship(back_populates="clips")
