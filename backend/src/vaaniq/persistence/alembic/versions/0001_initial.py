"""Initial VaaniQ persistence schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-10
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS = sa.text("(CURRENT_TIMESTAMP)")


def _created_at() -> sa.Column[object]:
    """Return a timezone-aware created_at column."""
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=_TS,
        nullable=False,
    )


def upgrade() -> None:
    """Create the Phase-1 persistence tables."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("git_sha", sa.String(length=64), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "human_study_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fluency_self_report", sa.String(length=256), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "experiment_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("metric_name", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("dims", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "models",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("uri", sa.String(length=1024), nullable=False),
        sa.Column("card", sa.JSON(), nullable=True),
        _created_at(),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "uploads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("compression_status", sa.String(length=64), nullable=False),
        sa.Column("storage_uri", sa.String(length=1024), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=False),
        _created_at(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "human_study_responses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("participant_id", sa.Uuid(), nullable=False),
        sa.Column("clip_id", sa.String(length=256), nullable=False),
        sa.Column("choice", sa.String(length=16), nullable=False),
        sa.Column("confidence_1_5", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["human_study_participants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "calibration_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("model_id", sa.Uuid(), nullable=False),
        sa.Column("temperatures", sa.JSON(), nullable=False),
        sa.Column("ece_pre", sa.Float(), nullable=False),
        sa.Column("ece_post", sa.Float(), nullable=False),
        _created_at(),
        sa.ForeignKeyConstraint(["model_id"], ["models.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "predictions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("upload_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reliability", sa.String(length=32), nullable=False),
        sa.Column("extras", sa.JSON(), nullable=True),
        _created_at(),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop all Phase-1 persistence tables."""
    op.drop_table("predictions")
    op.drop_table("calibration_runs")
    op.drop_table("human_study_responses")
    op.drop_table("uploads")
    op.drop_table("models")
    op.drop_table("experiment_metrics")
    op.drop_table("human_study_participants")
    op.drop_table("experiments")
    op.drop_table("users")
