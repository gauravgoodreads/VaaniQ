"""Dataset source port (REQ-101-104)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import DatasetSource


class DatasetSourcePort(ABC):
    """Iterate clips from an external corpus.

    Named ``DatasetSourcePort`` to avoid clashing with the ``DatasetSource``
    enum in ``vaaniq.core.types``. Serves REQ-101-104, REQ-130.
    Implementations: KathbathSource, etc. (ROADMAP-011).
    """

    @property
    @abstractmethod
    def source_id(self) -> DatasetSource:
        """Return the enum identity of this source."""

    @abstractmethod
    def iter_clips(self) -> Iterator[ClipMetadata]:
        """Yield clip metadata records from the corpus.

        Yields:
            ClipMetadata rows (audio fetched separately via ObjectStore/loader).
        """
