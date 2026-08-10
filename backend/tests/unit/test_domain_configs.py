"""Domain YAML inventory and schema tests (Phase 1 step 9)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vaaniq.config import (
    DOMAIN_CONFIG_FILES,
    AudioCompressionConfig,
    CalibrationConfig,
    DatasetSourceConfig,
    XlsrAasistConfig,
    find_configs_root,
    load_all_domain_configs,
    load_typed_yaml,
)
from vaaniq.core.errors import ConfigurationError
from vaaniq.core.types import Language


def test_domain_inventory_files_exist() -> None:
    root = find_configs_root()
    for rel in DOMAIN_CONFIG_FILES:
        assert (root / rel).is_file(), f"missing {rel}"


def test_load_all_domain_configs() -> None:
    loaded = load_all_domain_configs()
    assert set(loaded) == set(DOMAIN_CONFIG_FILES)
    assert isinstance(loaded["data/kathbath.yaml"], DatasetSourceConfig)
    assert isinstance(loaded["audio/compression.yaml"], AudioCompressionConfig)
    assert isinstance(loaded["calibration/temperature.yaml"], CalibrationConfig)


def test_xlsr_checkpoint_is_300m() -> None:
    """REQ-041 / OQ-027 — default XLS-R id is facebook/wav2vec2-xls-r-300m."""
    root = find_configs_root()
    cfg = load_typed_yaml(root / "model/xlsr_aasist.yaml", XlsrAasistConfig)
    assert cfg.xlsr_model_id == "facebook/wav2vec2-xls-r-300m"


def test_opus_defaults_match_oq007() -> None:
    """ASSUMPTION: OQ-007 provisional Opus defaults."""
    root = find_configs_root()
    cfg = load_typed_yaml(root / "audio/compression.yaml", AudioCompressionConfig)
    assert cfg.bitrate_kbps == 16
    assert cfg.sample_rate_hz == 16000
    assert cfg.application == "voip"
    assert cfg.additive_noise_enabled is False


def test_ece_bins_match_oq017() -> None:
    """ASSUMPTION: OQ-017 — 15 equal-width bins."""
    root = find_configs_root()
    cfg = load_typed_yaml(root / "calibration/temperature.yaml", CalibrationConfig)
    assert cfg.ece_n_bins == 15
    assert cfg.ece_binning == "equal_width"
    assert cfg.fit_per_language is True
    assert cfg.fit_per_condition is True


def test_dataset_languages_are_project_languages() -> None:
    loaded = load_all_domain_configs()
    allowed = set(Language)
    for rel, model in loaded.items():
        if not isinstance(model, DatasetSourceConfig):
            continue
        assert set(model.languages) <= allowed, rel
        assert "te" not in {lang.value for lang in model.languages}


def test_unknown_domain_key_fails(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("sample_rate_hz: 16000\nmystery: 1\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_typed_yaml(path, AudioCompressionConfig)


def test_split_ratios_must_sum_to_one(tmp_path: Path) -> None:
    path = tmp_path / "train.yaml"
    path.write_text(
        "\n".join(
            [
                "name: default",
                "seed: 42",
                "model_config: model/xlsr_aasist.yaml",
                "audio_preprocessing: audio/preprocessing.yaml",
                "audio_compression: audio/compression.yaml",
                "split_ratios:",
                "  train: 0.5",
                "  val: 0.5",
                "  test: 0.5",
                "speaker_disjoint: true",
                "languages: [hi, mr, ta]",
                "learning_rate: 0.0001",
                "batch_size: 24",
                "max_epochs: 1",
                "experiment_root: ./research/experiments",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_typed_yaml(path, DOMAIN_CONFIG_FILES["train/default.yaml"])
