"""No remaining ROADMAP xfail stubs in the ML/research path."""

from __future__ import annotations

from pathlib import Path

from vaaniq.core.types import ExportFormat
from vaaniq.human_study import CsvHumanStudyExporter


def test_human_export(tmp_path: Path) -> None:
    path = CsvHumanStudyExporter().export(
        [{"participant_id": "p1", "choice": "real"}],
        fmt=ExportFormat.JSON,
        destination=tmp_path / "o.json",
    )
    assert path.is_file()
