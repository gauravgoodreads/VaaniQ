"""Tests for master DOCX visual-audit helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from PIL import Image, ImageDraw


def _load_script() -> ModuleType:
    script = Path(__file__).resolve().parents[3] / "scripts" / "verify_master_docx.py"
    spec = importlib.util.spec_from_file_location("verify_master_docx", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load_script()


def test_figure_margin_audit_accepts_safe_content(tmp_path: Path) -> None:
    path = tmp_path / "safe.png"
    image = Image.new("RGB", (100, 100), "white")
    ImageDraw.Draw(image).rectangle((20, 20, 80, 80), fill="black")
    image.save(path)
    assert MODULE.verify_figure_margins([path]) == []


def test_figure_margin_audit_rejects_cropped_content(tmp_path: Path) -> None:
    path = tmp_path / "cropped.png"
    image = Image.new("RGB", (100, 100), "white")
    ImageDraw.Draw(image).rectangle((0, 20, 80, 80), fill="black")
    image.save(path)
    failures = MODULE.verify_figure_margins([path])
    assert len(failures) == 1
    assert "cropped.png" in failures[0]
