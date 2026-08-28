"""Tests for the real publication-corpus preparation helpers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_script() -> ModuleType:
    script = Path(__file__).resolve().parents[3] / "scripts" / "prepare_publication_corpus.py"
    spec = importlib.util.spec_from_file_location("prepare_publication_corpus", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load_script()


def test_speaker_split_is_deterministic_and_source_independent() -> None:
    split = MODULE.speaker_split("spk-42", seed=42)
    assert split in {"train", "val", "test"}
    assert MODULE.speaker_split("spk-42", seed=42) == split


def test_speaker_split_approximately_respects_ratios() -> None:
    counts = {"train": 0, "val": 0, "test": 0}
    for index in range(10_000):
        counts[MODULE.speaker_split(f"spk-{index}", seed=42)] += 1
    assert counts["train"] == pytest.approx(7_000, abs=200)
    assert counts["val"] == pytest.approx(1_500, abs=150)
    assert counts["test"] == pytest.approx(1_500, abs=150)


def test_resample_mono_normalizes_and_trims() -> None:
    stereo = np.column_stack(
        [
            np.linspace(-0.5, 0.5, 32_000, dtype=np.float32),
            np.linspace(-0.25, 0.25, 32_000, dtype=np.float32),
        ]
    )
    output = MODULE.resample_mono(
        stereo,
        32_000,
        target_rate=16_000,
        max_duration_sec=0.5,
    )
    assert output.dtype == np.float32
    assert output.shape == (8_000,)
    assert float(np.max(np.abs(output))) == pytest.approx(0.95, abs=1e-5)


def test_resample_rejects_empty_audio() -> None:
    with pytest.raises(ValueError, match="empty"):
        MODULE.resample_mono(
            np.asarray([], dtype=np.float32),
            16_000,
            target_rate=16_000,
            max_duration_sec=1.0,
        )


def test_opus_augmentation_preserves_pair_and_split(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "corpus"
    source = root / "audio" / "hi" / "real" / "hi-real.flac"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"test-audio")
    manifest = root / "manifest.jsonl"
    manifest.write_text(
        json.dumps(
            {
                "clip_id": "hi-real",
                "language": "hi",
                "label": "real",
                "compression_status": "clean",
                "sample_rate_hz": 16_000,
                "duration_sec": 2.0,
                "split": "test",
                "dataset_source": "ai4bharat/Kathbath",
                "source": "kathbath",
                "speaker_id": "spk-1",
                "uri": "audio/hi/real/hi-real.flac",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "provenance.json").write_text("{}", encoding="utf-8")

    def fake_run(command: list[str], *, check: bool) -> None:
        assert check
        source_path = Path(command[command.index("-i") + 1])
        Path(command[-1]).write_bytes(source_path.read_bytes())

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)
    monkeypatch.setattr("imageio_ffmpeg.get_ffmpeg_exe", lambda: "ffmpeg")
    MODULE.augment_evaluation_with_opus(root)

    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert {row["compression_status"] for row in rows} == {
        "clean",
        "opus_whatsapp_sim",
    }
    assert {row["split"] for row in rows} == {"test"}
    assert {row["speaker_id"] for row in rows} == {"spk-1"}
    assert {row["pair_id"] for row in rows} == {"hi-real"}
