"""Drop human-study tables (feature removed from the app).

Revision ID: 0005_drop_human_study
Revises: 0004_query_indexes
Create Date: 2026-10-30
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_drop_human_study"
down_revision: str | None = "0004_query_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS = sa.text("(CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Drop the human-study responses/participants tables."""
    op.drop_index("ix_human_study_responses_participant_id", table_name="human_study_responses")
    op.drop_table("human_study_responses")
    op.drop_table("human_study_participants")


def downgrade() -> None:
    """Recreate the human-study tables as of revision 0004 (data is not restored)."""
    op.create_table(
        "human_study_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fluency_self_report", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_TS, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "human_study_responses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("participant_id", sa.Uuid(), nullable=False),
        sa.Column("clip_id", sa.String(length=256), nullable=False),
        sa.Column("choice", sa.String(length=16), nullable=False),
        sa.Column("confidence_1_5", sa.Integer(), nullable=False),
        sa.Column("response_ms", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column("compression_status", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["human_study_participants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_human_study_responses_participant_id",
        "human_study_responses",
        ["participant_id"],
    )
