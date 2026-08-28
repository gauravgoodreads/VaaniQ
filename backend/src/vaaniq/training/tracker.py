"""File-based experiment tracker (ROADMAP-030 / REQ-137-138)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast

import structlog

from vaaniq.core.domain.entities import ExperimentManifest
from vaaniq.core.ports.experiment_tracker import ExperimentTracker

log = structlog.get_logger(__name__)


class _ScalarWriter(Protocol):
    """Typed subset of TensorBoard SummaryWriter used by the tracker."""

    def add_scalar(self, name: str, value: float, *, global_step: int) -> None:
        """Write one scalar event."""


class FileExperimentTracker(ExperimentTracker):
    """Write metrics JSONL + manifests under ``research/experiments``."""

    def __init__(self, root: Path | None = None, experiment_id: str | None = None) -> None:
        """Bind experiment root.

        Args:
            root: Experiment root directory.
            experiment_id: Optional fixed id; otherwise created on first write.
        """
        self._root = Path(root) if root is not None else Path("./research/experiments")
        self._experiment_id = experiment_id
        self._metrics_path: Path | None = None
        self._tb_writer: _ScalarWriter | None = None

    @property
    def experiment_id(self) -> str:
        """Return active experiment id."""
        if self._experiment_id is None:
            self._experiment_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return self._experiment_id

    def _dir(self) -> Path:
        d = self._root / self.experiment_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def log_metric(
        self,
        name: str,
        value: float,
        *,
        dims: Mapping[str, str] | None = None,
    ) -> None:
        """Append a metric row to JSONL and optional TensorBoard."""
        path = self._dir() / "metrics.jsonl"
        row = {
            "name": name,
            "value": value,
            "dims": dict(dims or {}),
            "ts": datetime.now(UTC).isoformat(),
        }
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        self._metrics_path = path
        self._tb_scalar(name, value)
        log.info("metric_logged", name=name, value=value, experiment_id=self.experiment_id)

    def write_manifest(self, manifest: ExperimentManifest) -> None:
        """Persist run manifest beside experiment artefacts."""
        path = self._dir() / "manifest.json"
        payload = {
            "experiment_id": manifest.experiment_id,
            "git_sha": manifest.git_sha,
            "dirty": manifest.dirty,
            "seed": manifest.seed,
            "config": dict(manifest.config),
            "package_versions": dict(manifest.package_versions),
            "hardware": dict(manifest.hardware),
            "dataset_checksums": dict(manifest.dataset_checksums),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log.info("manifest_written", path=str(path))

    def list_experiments(self) -> list[str]:
        """List experiment directory names."""
        if not self._root.is_dir():
            return []
        return sorted(p.name for p in self._root.iterdir() if p.is_dir())

    def _tb_scalar(self, name: str, value: float) -> None:
        """Best-effort TensorBoard scalar (optional ``[ml]``)."""
        try:
            from torch.utils.tensorboard.writer import SummaryWriter
        except Exception:
            # Fallback: write TB-compatible CSV
            tb_csv = self._dir() / "tensorboard_scalars.csv"
            if not tb_csv.is_file():
                tb_csv.write_text("tag,value\n", encoding="utf-8")
            with tb_csv.open("a", encoding="utf-8") as fh:
                fh.write(f"{name},{value}\n")
            return
        if self._tb_writer is None:
            writer_factory = cast("Callable[..., _ScalarWriter]", SummaryWriter)
            self._tb_writer = writer_factory(log_dir=str(self._dir() / "tb"))
        writer = self._tb_writer
        assert writer is not None
        step = sum(1 for _ in (self._dir() / "metrics.jsonl").open(encoding="utf-8"))
        writer.add_scalar(name, value, global_step=step)
