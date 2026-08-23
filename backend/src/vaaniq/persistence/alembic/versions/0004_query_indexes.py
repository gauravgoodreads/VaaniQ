"""Add lookup indexes for clip, prediction, and study queries.

Revision ID: 0004_query_indexes
Revises: 0003_human_study_timing
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0004_query_indexes"
down_revision: str | None = "0003_human_study_timing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create additive secondary indexes (safe; no data rewrite)."""
    op.create_index("ix_uploads_language", "uploads", ["language"])
    op.create_index("ix_uploads_storage_uri", "uploads", ["storage_uri"])
    op.create_index("ix_predictions_upload_id", "predictions", ["upload_id"])
    op.create_index(
        "ix_experiment_metrics_experiment_id",
        "experiment_metrics",
        ["experiment_id"],
    )
    op.create_index("ix_calibration_runs_model_id", "calibration_runs", ["model_id"])
    op.create_index(
        "ix_human_study_responses_participant_id",
        "human_study_responses",
        ["participant_id"],
    )
    op.create_index("ix_audio_clips_clip_id", "audio_clips", ["clip_id"], unique=True)
    op.create_index("ix_audio_clips_language", "audio_clips", ["language"])
    op.create_index("ix_audio_clips_split", "audio_clips", ["split"])
    op.create_index("ix_audio_clips_speaker_id", "audio_clips", ["speaker_id"])
    op.create_index("ix_audio_clips_dataset_id", "audio_clips", ["dataset_id"])


def downgrade() -> None:
    """Drop secondary indexes added in this revision."""
    op.drop_index("ix_audio_clips_dataset_id", table_name="audio_clips")
    op.drop_index("ix_audio_clips_speaker_id", table_name="audio_clips")
    op.drop_index("ix_audio_clips_split", table_name="audio_clips")
    op.drop_index("ix_audio_clips_language", table_name="audio_clips")
    op.drop_index("ix_audio_clips_clip_id", table_name="audio_clips")
    op.drop_index("ix_human_study_responses_participant_id", table_name="human_study_responses")
    op.drop_index("ix_calibration_runs_model_id", table_name="calibration_runs")
    op.drop_index("ix_experiment_metrics_experiment_id", table_name="experiment_metrics")
    op.drop_index("ix_predictions_upload_id", table_name="predictions")
    op.drop_index("ix_uploads_storage_uri", table_name="uploads")
    op.drop_index("ix_uploads_language", table_name="uploads")
