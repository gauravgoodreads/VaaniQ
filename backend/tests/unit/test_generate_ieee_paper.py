"""Tests for IEEE paper generation helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from docx import Document


def _load_script() -> ModuleType:
    script = Path(__file__).resolve().parents[3] / "scripts" / "generate_ieee_paper_docx.py"
    spec = importlib.util.spec_from_file_location("generate_ieee_paper_docx", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load_script()


def test_number_rejects_non_numeric_values() -> None:
    assert MODULE._number({"value": 0.75}, "value") == 0.75
    assert MODULE._number({"value": "0.75"}, "value") == 0.0


def test_set_columns_writes_two_column_section() -> None:
    document = Document()
    section = document.sections[0]
    MODULE._set_columns(section, 2)
    columns = section._sectPr.xpath("./w:cols")
    assert len(columns) == 1
    assert (
        columns[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num") == "2"
    )
