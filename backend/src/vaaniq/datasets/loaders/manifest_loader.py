"""Load ClipMetadata from local JSONL/JSON manifests (ROADMAP-011)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import DatasetError
from vaaniq.datasets.manifests.clip_schema import parse_clip_metadata
from vaaniq.observability.logging import get_logger

log = get_logger(__name__)


class ManifestClipLoader:
    """Yield ``ClipMetadata`` rows from a local JSONL or JSON array file.

    Never performs network I/O. Serves ROADMAP-011 / ROADMAP-012.
    """

    def iter_clips(self, manifest_path: Path) -> Iterator[ClipMetadata]:
        """Iterate validated clips from ``manifest_path``.

        Args:
            manifest_path: Path to a ``.jsonl`` file or a JSON array document.

        Yields:
            Validated ``ClipMetadata`` records.

        Raises:
            DatasetError: If the file is missing or has an unsupported shape.
        """
        if not manifest_path.is_file():
            msg = f"manifest not found: {manifest_path}"
            raise DatasetError(msg)
        suffix = manifest_path.suffix.lower()
        if suffix == ".jsonl":
            yield from self._iter_jsonl(manifest_path)
            return
        if suffix == ".json":
            yield from self._iter_json(manifest_path)
            return
        msg = f"unsupported manifest suffix: {manifest_path.suffix}"
        raise DatasetError(msg)

    def _iter_jsonl(self, path: Path) -> Iterator[ClipMetadata]:
        """Parse newline-delimited JSON objects."""
        count = 0
        with path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                raw = json.loads(stripped)
                if not isinstance(raw, dict):
                    msg = f"{path}:{line_no}: expected JSON object"
                    raise DatasetError(msg)
                yield parse_clip_metadata(raw)
                count += 1
        log.info("manifest_loaded", path=str(path), clip_count=count, format="jsonl")

    def _iter_json(self, path: Path) -> Iterator[ClipMetadata]:
        """Parse a JSON array of objects."""
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            msg = f"{path}: expected a JSON array of clip objects"
            raise DatasetError(msg)
        count = 0
        for index, raw in enumerate(payload):
            if not isinstance(raw, dict):
                msg = f"{path}: entry {index} is not an object"
                raise DatasetError(msg)
            yield parse_clip_metadata(raw)
            count += 1
        log.info("manifest_loaded", path=str(path), clip_count=count, format="json")
