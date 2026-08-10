"""Generic repository port for persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    """CRUD port for aggregate roots.

    Concrete SQLAlchemy repositories implement this in ROADMAP-006.
    """

    @abstractmethod
    def get(self, entity_id: ID) -> T | None:
        """Fetch an entity by id."""

    @abstractmethod
    def add(self, entity: T) -> T:
        """Persist a new entity and return it (possibly with generated id)."""

    @abstractmethod
    def delete(self, entity_id: ID) -> None:
        """Delete an entity by id."""
