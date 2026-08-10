"""Engine and session factory (ROADMAP-006).

ASSUMPTION: OQ-021 — SQLite by default; PostgreSQL-compatible SQLAlchemy types.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_db_engine(database_url: str, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine.

    Args:
        database_url: SQLAlchemy URL (sqlite or postgresql).
        echo: Echo SQL when True.
    """
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, echo=echo, future=True, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory bound to ``engine``."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
