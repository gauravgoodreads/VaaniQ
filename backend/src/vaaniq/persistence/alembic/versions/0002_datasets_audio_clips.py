"""Add datasets catalog and audio_clips tables.

Revision ID: 0002_datasets_audio_clips
Revises: 0001_initial
Create Date: 2026-08-12
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_datasets_audio_clips"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS = sa.text("(CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Create ``datasets`` and ``audio_clips`` (ROADMAP-011 / ROADMAP-012)."""
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("gated", sa.Integer(), nullable=False),
        sa.Column("licence_note", sa.String(length=1024), nullable=True),
        sa.Column("config_relpath", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=_TS,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "audio_clips",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=True),
        sa.Column("clip_id", sa.String(length=256), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=16), nullable=False),
        sa.Column("compression_status", sa.String(length=64), nullable=False),
        sa.Column("sample_rate_hz", sa.Integer(), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=False),
        sa.Column("split", sa.String(length=16), nullable=False),
        sa.Column("dataset_source", sa.String(length=512), nullable=False),
        sa.Column("speaker_id", sa.String(length=256), nullable=True),
        sa.Column("attack_type", sa.String(length=64), nullable=True),
        sa.Column("generation_model", sa.String(length=256), nullable=True),
        sa.Column("pair_id", sa.String(length=256), nullable=True),
        sa.Column("consent_ref", sa.String(length=512), nullable=True),
        # ASSUMPTION: OQ-036
        sa.Column("gender", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("speaker_age", sa.Integer(), nullable=True),
        sa.Column("emotion", sa.String(length=64), nullable=True),
        sa.Column("recording_medium", sa.String(length=128), nullable=True),
        sa.Column("quality", sa.String(length=64), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("uri", sa.String(length=1024), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop ``audio_clips`` then ``datasets``."""
    op.drop_table("audio_clips")
    op.drop_table("datasets")
