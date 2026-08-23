"""Searchable experiment store (Phase 4 / REQ-137)."""

from __future__ import annotations

import json
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from vaaniq.research.records import ResearchRunRecord
from vaaniq.training.trainer import _git_sha

log = structlog.get_logger(__name__)


def collect_hardware() -> dict[str, str]:
    """Collect host hardware strings for run manifests."""
    info = {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python": platform.python_version(),
    }
    try:
        import torch

        info["torch"] = str(torch.__version__)
        info["cuda"] = str(torch.cuda.is_available())
    except Exception:
        log.warning("torch_probe_failed")
        info["torch"] = "absent"
        info["cuda"] = "false"
    return info


class ExperimentStore:
    """JSONL catalogue of ``ResearchRunRecord`` under ``research/experiments``."""

    def __init__(self, root: Path | None = None) -> None:
        """Bind catalogue root."""
        self._root = Path(root) if root is not None else Path("./research/experiments")
        self._root.mkdir(parents=True, exist_ok=True)
        self._index = self._root / "index.jsonl"

    def put(self, record: ResearchRunRecord) -> Path:
        """Append to the index and write ``record.json`` beside the run dir."""
        run_dir = self._root / record.experiment_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "record.json"
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        with self._index.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict()) + "\n")
        log.info("research_record_stored", experiment_id=record.experiment_id)
        return path

    def list_records(self) -> list[ResearchRunRecord]:
        """Load all indexed records (last write wins per id)."""
        if not self._index.is_file():
            return []
        by_id: dict[str, ResearchRunRecord] = {}
        for line in self._index.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = ResearchRunRecord.from_dict(json.loads(line))
            by_id[rec.experiment_id] = rec
        return sorted(by_id.values(), key=lambda r: r.timestamp)

    def search(
        self,
        *,
        language: str | None = None,
        model_version: str | None = None,
        rq_id: str | None = None,
    ) -> list[ResearchRunRecord]:
        """Filter records by language, model, or research-question id."""
        out: list[ResearchRunRecord] = []
        for rec in self.list_records():
            if language is not None and language not in rec.languages:
                continue
            if model_version is not None and rec.model_version != model_version:
                continue
            if rq_id is not None and rq_id not in rec.rq_ids:
                continue
            out.append(rec)
        return out

    def compare(self, metric: str) -> list[dict[str, Any]]:
        """Return rows for experiment comparison tables."""
        rows: list[dict[str, Any]] = []
        for rec in self.list_records():
            rows.append(
                {
                    "experiment_id": rec.experiment_id,
                    "model_version": rec.model_version,
                    "languages": ",".join(rec.languages),
                    "compression_settings": rec.compression_settings,
                    "seed": rec.seed,
                    metric: rec.metrics.get(metric),
                }
            )
        return rows

    def now_iso(self) -> str:
        """UTC timestamp helper."""
        return datetime.now(UTC).isoformat()

    def git_sha(self) -> str:
        """Resolved git SHA (unknown if git missing)."""
        sha, _dirty = _git_sha()
        return sha
