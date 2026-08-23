"""Add timing/language columns to human_study_responses.

Revision ID: 0003_human_study_timing
Revises: 0002_datasets_audio_clips
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_human_study_timing"
down_revision: str | None = "0002_datasets_audio_clips"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add optional response timing and slice columns (ROADMAP-059)."""
    op.add_column("human_study_responses", sa.Column("response_ms", sa.Integer(), nullable=True))
    op.add_column(
        "human_study_responses", sa.Column("language", sa.String(length=8), nullable=True)
    )
    op.add_column(
        "human_study_responses",
        sa.Column("compression_status", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    """Drop optional human-study columns."""
    op.drop_column("human_study_responses", "compression_status")
    op.drop_column("human_study_responses", "language")
    op.drop_column("human_study_responses", "response_ms")
