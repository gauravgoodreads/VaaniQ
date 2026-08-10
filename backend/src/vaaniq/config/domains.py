"""Typed domain configuration models for experiment YAMLs (Phase 1 step 9).

These are separate from ``AppConfig`` so pipeline knobs are not merged into
the runtime app settings object (``extra='forbid'``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from vaaniq.core.types import DatasetSource, Label, Language

SplitPolicy = Literal["speaker_disjoint"]
Pooling = Literal["mean", "max", "cls"]
TransformerLayer = Literal["last"]
EceBinning = Literal["equal_width", "equal_mass"]
FitSplit = Literal["val"]


class DatasetSourceConfig(BaseModel):
    """Corpus adapter config under ``configs/data/*.yaml`` (ROADMAP-011)."""

    model_config = ConfigDict(extra="forbid")

    source_id: DatasetSource
    hf_dataset_id: str | None = None
    local_root: Path | None = None
    gated: bool = False
    languages: list[Language]
    label: Label
    # ASSUMPTION: OQ-002
    target_hours_per_language: float | None = None
    # ASSUMPTION: OQ-005
    target_minutes_per_language: float | None = None
    split_policy: SplitPolicy = "speaker_disjoint"
    require_consent_ref: bool = False
    allow_mirror: bool = False
    mirror_dataset_id: str | None = None
    licence_note: str | None = None
    notes: str | None = None

    @field_validator("languages")
    @classmethod
    def _languages_nonempty(cls, value: list[Language]) -> list[Language]:
        """Reject empty language lists for corpus configs."""
        if not value:
            msg = "languages must be non-empty for dataset sources"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _require_location(self) -> DatasetSourceConfig:
        """Require HF id or local root."""
        if self.hf_dataset_id is None and self.local_root is None:
            msg = "either hf_dataset_id or local_root is required"
            raise ValueError(msg)
        return self


class AudioPreprocessingConfig(BaseModel):
    """``configs/audio/preprocessing.yaml`` (ROADMAP-020 / REQ-098)."""

    model_config = ConfigDict(extra="forbid")

    # ASSUMPTION: OQ-007
    sample_rate_hz: int = 16000
    mono: bool = True
    trim_silence: bool = True
    normalize_peak: bool = True
    target_peak: float = 0.95
    min_duration_sec: float = 0.5
    max_duration_sec: int = 120


class AudioCompressionConfig(BaseModel):
    """``configs/audio/compression.yaml`` (ROADMAP-021 / OQ-007)."""

    model_config = ConfigDict(extra="forbid")

    codec: str = "libopus"
    # ASSUMPTION: OQ-007
    bitrate_kbps: int = 16
    application: str = "voip"
    sample_rate_hz: int = 16000
    channels: int = 1
    container: str = "ogg"
    pair_clean_and_compressed: bool = True
    # ASSUMPTION: OQ-023
    additive_noise_enabled: bool = False
    additive_noise_snr_db: float | None = None
    # ASSUMPTION: OQ-012
    enable_bitrate_ladder: bool = False
    bitrate_ladder_kbps: list[int] = Field(default_factory=lambda: [8, 16, 24])


class XlsrAasistConfig(BaseModel):
    """``configs/model/xlsr_aasist.yaml`` (REQ-041, OQ-013, OQ-014)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["xlsr_aasist"] = "xlsr_aasist"
    xlsr_model_id: str = "facebook/wav2vec2-xls-r-300m"
    freeze_frontend: bool = True
    # ASSUMPTION: OQ-013
    pooling: Pooling = "mean"
    transformer_layer: TransformerLayer = "last"
    window_sec: float = 4.0
    hop_sec: float = 2.0
    # ASSUMPTION: OQ-014
    learning_rate: float = 0.0001
    batch_size: int = 24
    max_epochs: int = 100
    weight_decay: float = 0.0001
    loss: str = "cross_entropy"
    checkpoint_dir: Path = Path("./models/checkpoints/xlsr_aasist")


class LfccGmmConfig(BaseModel):
    """``configs/model/lfcc_gmm.yaml`` (ROADMAP-031 / REQ-042)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["lfcc_gmm"] = "lfcc_gmm"
    n_lfcc: int = 60
    n_fft: int = 512
    hop_length: int = 160
    win_length: int = 400
    sample_rate_hz: int = 16000
    n_components: int = 512
    covariance_type: str = "diag"
    checkpoint_dir: Path = Path("./models/checkpoints/lfcc_gmm")


class RawNet2Config(BaseModel):
    """``configs/model/rawnet2.yaml`` (ROADMAP-032 / REQ-043)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["rawnet2"] = "rawnet2"
    sample_rate_hz: int = 16000
    # ASSUMPTION: OQ-014-style placeholders
    learning_rate: float = 0.0001
    batch_size: int = 32
    max_epochs: int = 100
    weight_decay: float = 0.0001
    checkpoint_dir: Path = Path("./models/checkpoints/rawnet2")


class SplitRatios(BaseModel):
    """Train/val/test fractions (ASSUMPTION: OQ-008)."""

    model_config = ConfigDict(extra="forbid")

    train: float = 0.70
    val: float = 0.15
    test: float = 0.15

    @model_validator(mode="after")
    def _sum_to_one(self) -> SplitRatios:
        """Require ratios to sum to ~1."""
        total = self.train + self.val + self.test
        if abs(total - 1.0) > 1e-6:
            msg = f"split_ratios must sum to 1.0, got {total}"
            raise ValueError(msg)
        return self


class TrainDefaultConfig(BaseModel):
    """``configs/train/default.yaml`` (ROADMAP-030)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["default"] = "default"
    seed: int = 42
    model_config_path: str = Field(alias="model_config")
    audio_preprocessing: str
    audio_compression: str
    split_ratios: SplitRatios
    speaker_disjoint: bool = True
    languages: list[Language]
    learning_rate: float
    batch_size: int
    max_epochs: int
    num_workers: int = 0
    deterministic: bool = True
    experiment_root: Path


class TrainCvConfig(BaseModel):
    """``configs/train/cv.yaml`` (ROADMAP-030)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["cv"] = "cv"
    seed: int = 42
    model_config_path: str = Field(alias="model_config")
    audio_preprocessing: str
    audio_compression: str
    # ASSUMPTION: OQ-008
    n_folds: int = 5
    speaker_disjoint: bool = True
    languages: list[Language]
    learning_rate: float
    batch_size: int
    max_epochs: int
    num_workers: int = 0
    deterministic: bool = True
    experiment_root: Path


class TrainEnglishOnlyConfig(BaseModel):
    """``configs/train/english_only.yaml`` (ROADMAP-033 / OQ-015)."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["english_only"] = "english_only"
    seed: int = 42
    model_config_path: str = Field(alias="model_config")
    audio_preprocessing: str
    audio_compression: str
    # ASSUMPTION: OQ-015
    asvspoof_subset: str
    asvspoof_split: str
    languages: list[Language] = Field(default_factory=list)
    learning_rate: float
    batch_size: int
    max_epochs: int
    num_workers: int = 0
    deterministic: bool = True
    experiment_root: Path
    notes: str | None = None


class EvalProfileConfig(BaseModel):
    """``configs/eval/*.yaml`` (ROADMAP-036+)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    metrics: list[str]
    matrices: list[str]
    slices: list[str]
    # ASSUMPTION: OQ-009
    bootstrap_ci: bool = True
    bootstrap_samples: int = 1000
    ci_level: float = 0.95
    report_dir: Path
    notes: str | None = None


class ReliabilityBadgeConfig(BaseModel):
    """Reliability badge thresholds (ASSUMPTION: OQ-010)."""

    model_config = ConfigDict(extra="forbid")

    moderate_confidence_low: float = 0.55
    moderate_confidence_high: float = 0.70
    flag_opus_as_moderate: bool = True


class CalibrationConfig(BaseModel):
    """``configs/calibration/temperature.yaml`` (ROADMAP-043 / OQ-017, OQ-031)."""

    model_config = ConfigDict(extra="forbid")

    method: Literal["temperature_scaling"] = "temperature_scaling"
    fit_per_language: bool = True
    fit_per_condition: bool = True
    fit_split: FitSplit = "val"
    # ASSUMPTION: OQ-017
    ece_n_bins: int = 15
    ece_binning: EceBinning = "equal_width"
    reliability: ReliabilityBadgeConfig = Field(default_factory=ReliabilityBadgeConfig)
    artefact_dir: Path
