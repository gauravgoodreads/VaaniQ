"""Load typed domain YAML configs from the repo ``configs/`` tree."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from vaaniq.config.domains import (
    AudioCompressionConfig,
    AudioPreprocessingConfig,
    CalibrationConfig,
    DatasetSourceConfig,
    EvalProfileConfig,
    HumanStudyProtocolConfig,
    LfccGmmConfig,
    RawNet2Config,
    ResearchConditionsConfig,
    TrainCvConfig,
    TrainDefaultConfig,
    TrainEnglishOnlyConfig,
    XlsrAasistConfig,
)
from vaaniq.core.errors import ConfigurationError

T = TypeVar("T", bound=BaseModel)

# Relative paths under configs/ → pydantic model (Phase 1 step 9 inventory).
DOMAIN_CONFIG_FILES: dict[str, type[BaseModel]] = {
    "data/kathbath.yaml": DatasetSourceConfig,
    "data/indicvoices_r.yaml": DatasetSourceConfig,
    "data/common_voice.yaml": DatasetSourceConfig,
    "data/indicsynth.yaml": DatasetSourceConfig,
    "data/team_recordings.yaml": DatasetSourceConfig,
    "data/generated_audio.yaml": DatasetSourceConfig,
    "audio/preprocessing.yaml": AudioPreprocessingConfig,
    "audio/compression.yaml": AudioCompressionConfig,
    "model/xlsr_aasist.yaml": XlsrAasistConfig,
    "model/lfcc_gmm.yaml": LfccGmmConfig,
    "model/rawnet2.yaml": RawNet2Config,
    "train/default.yaml": TrainDefaultConfig,
    "train/cv.yaml": TrainCvConfig,
    "train/english_only.yaml": TrainEnglishOnlyConfig,
    "eval/full.yaml": EvalProfileConfig,
    "eval/zero_shot.yaml": EvalProfileConfig,
    "eval/cross_condition.yaml": EvalProfileConfig,
    "eval/research_conditions.yaml": ResearchConditionsConfig,
    "calibration/temperature.yaml": CalibrationConfig,
    "human_study/protocol.yaml": HumanStudyProtocolConfig,
}


def find_configs_root(start: Path | None = None) -> Path:
    """Locate the repository ``configs/`` directory.

    Args:
        start: Optional starting path; walks parents looking for ``configs/base.yaml``.

    Raises:
        ConfigurationError: If the configs root cannot be found.
    """
    here = start if start is not None else Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "configs" / "base.yaml"
        if candidate.is_file():
            return parent / "configs"
    msg = "could not locate configs/base.yaml"
    raise ConfigurationError(msg)


def load_typed_yaml(path: Path, model_type: type[T]) -> T:
    """Parse ``path`` as YAML and validate as ``model_type``.

    Args:
        path: YAML file path.
        model_type: Pydantic model class.

    Raises:
        ConfigurationError: On missing file, bad YAML, or validation failure.
    """
    if not path.is_file():
        msg = f"config file not found: {path}"
        raise ConfigurationError(msg)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        msg = f"config root must be a mapping: {path}"
        raise ConfigurationError(msg)
    try:
        return model_type.model_validate(raw)
    except ValidationError as exc:
        raise ConfigurationError(f"{path}: {exc}") from exc


def load_all_domain_configs(
    configs_root: Path | None = None,
) -> dict[str, BaseModel]:
    """Load and validate every inventoried domain YAML.

    Args:
        configs_root: Optional override; defaults to repo ``configs/``.

    Returns:
        Mapping of relative path → validated model instance.
    """
    root = configs_root if configs_root is not None else find_configs_root()
    loaded: dict[str, BaseModel] = {}
    for rel, model_type in DOMAIN_CONFIG_FILES.items():
        loaded[rel] = load_typed_yaml(root / rel, model_type)
    return loaded
