"""Tests for persistence models and Alembic migrations (ROADMAP-006)."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select

from vaaniq.core.types import CompressionCondition, Label, Language, ReliabilityLevel
from vaaniq.persistence import (
    ExperimentRow,
    PredictionRow,
    UploadRow,
    UserRow,
    create_db_engine,
    create_session_factory,
    session_scope,
)

EXPECTED_TABLES = {
    "users",
    "uploads",
    "predictions",
    "experiments",
    "experiment_metrics",
    "models",
    "calibration_runs",
    "human_study_participants",
    "human_study_responses",
    "alembic_version",
}


def _backend_root() -> Path:
    """Return the backend package root (contains alembic.ini)."""
    return Path(__file__).resolve().parents[2]


def _alembic_config(db_url: str) -> Config:
    """Build an Alembic Config pointed at a temporary database."""
    ini = _backend_root() / "alembic.ini"
    cfg = Config(str(ini))
    cfg.set_main_option("sqlalchemy.url", db_url)
    # Ensure env.py can import the installed package
    cfg.set_main_option("prepend_sys_path", str(_backend_root() / "src"))
    return cfg


def test_alembic_upgrade_and_downgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``alembic upgrade head`` then ``downgrade base`` both succeed."""
    db_path = tmp_path / "vaaniq_test.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("VAANIQ_DATABASE_URL", db_url)
    cfg = _alembic_config(db_url)

    command.upgrade(cfg, "head")
    engine = create_db_engine(db_url)
    tables = set(inspect(engine).get_table_names())
    assert EXPECTED_TABLES.issubset(tables)

    command.downgrade(cfg, "base")
    tables_after = set(inspect(engine).get_table_names())
    assert "users" not in tables_after
    assert "uploads" not in tables_after


def test_orm_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Insert user → upload → prediction via ORM after migrations."""
    db_path = tmp_path / "orm.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("VAANIQ_DATABASE_URL", db_url)
    command.upgrade(_alembic_config(db_url), "head")

    engine = create_db_engine(db_url)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        user = UserRow(role="researcher")
        session.add(user)
        session.flush()
        upload = UploadRow(
            user_id=user.id,
            language=Language.HI.value,
            compression_status=CompressionCondition.CLEAN.value,
            storage_uri="file://tmp/a.wav",
            duration_sec=1.5,
        )
        session.add(upload)
        session.flush()
        pred = PredictionRow(
            upload_id=upload.id,
            label=Label.FAKE.value,
            confidence=0.91,
            reliability=ReliabilityLevel.MODERATE.value,
            extras={"source": "unit"},
        )
        session.add(pred)

    with session_scope(factory) as session:
        rows = session.scalars(select(PredictionRow)).all()
        assert len(rows) == 1
        assert rows[0].label == Label.FAKE.value
        assert rows[0].upload.language == Language.HI.value


def test_experiment_row_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Experiment config JSON persists."""
    db_path = tmp_path / "exp.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("VAANIQ_DATABASE_URL", db_url)
    command.upgrade(_alembic_config(db_url), "head")
    factory = create_session_factory(create_db_engine(db_url))

    with session_scope(factory) as session:
        session.add(
            ExperimentRow(
                name="smoke",
                git_sha="deadbeef",
                config={"seed": 42},
                seed=42,
            )
        )

    with session_scope(factory) as session:
        exp = session.scalars(select(ExperimentRow)).one()
        assert exp.config["seed"] == 42
