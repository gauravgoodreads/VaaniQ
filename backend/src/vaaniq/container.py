"""Composition root — constructs adapters from config (Phase 1 step 8).

No global singletons (vaaniq-core.mdc).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import structlog

from vaaniq.audio.compression.ffmpeg_opus import FFmpegOpusCompressor
from vaaniq.audio.io.soundfile_loader import SoundFileLoader
from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.audio.transforms.validator import MagicByteValidator
from vaaniq.calibration.temperature import TemperatureScaler
from vaaniq.config.models import AppConfig
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.ports.audio_loader import AudioLoader
from vaaniq.core.ports.audio_validator import AudioValidator
from vaaniq.core.ports.calibrator import Calibrator
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.ports.compressor import Compressor
from vaaniq.core.ports.embedding_cache import EmbeddingCache
from vaaniq.core.ports.experiment_tracker import ExperimentTracker
from vaaniq.core.ports.explainer import Explainer
from vaaniq.core.ports.feature_extractor import FeatureExtractor
from vaaniq.core.ports.human_study_exporter import HumanStudyExporter
from vaaniq.core.ports.object_store import ObjectStore
from vaaniq.core.ports.preprocessor import Preprocessor
from vaaniq.explainability.freq_importance import CompositeExplainer
from vaaniq.features.acoustic import acoustic_embedding
from vaaniq.features.cache.filesystem import FilesystemEmbeddingCache
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor
from vaaniq.human_study.exporter import CsvHumanStudyExporter
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.registry import ModelRegistry
from vaaniq.storage.local import LocalObjectStore
from vaaniq.training.tracker import FileExperimentTracker


def _stats_embedding_backend(wav: Waveform) -> np.ndarray:
    """Deterministic acoustic embedding without HF XLS-R weights (CI / local)."""
    return acoustic_embedding(wav, dim=1024)


def _default_checkpoint_path() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "models"
        / "checkpoints"
        / "xlsr_aasist"
        / "aasist-v1.npz"
    )


@dataclass(frozen=True, slots=True)
class AppContainer:
    """Immutable DI container holding port implementations.

    Construct via ``build_container`` — do not instantiate ad hoc in handlers.
    """

    config: AppConfig
    audio_loader: AudioLoader
    audio_validator: AudioValidator
    preprocessor: Preprocessor
    compressor: Compressor
    feature_extractor: FeatureExtractor
    embedding_cache: EmbeddingCache
    classifier: Classifier
    calibrator: Calibrator
    explainer: Explainer
    object_store: ObjectStore
    experiment_tracker: ExperimentTracker
    human_study_exporter: HumanStudyExporter
    model_registry: ModelRegistry


def build_container(config: AppConfig) -> AppContainer:
    """Build the application composition root from ``config``.

    Args:
        config: Loaded application configuration.

    Returns:
        AppContainer with concrete adapters for the ML pipeline.
    """
    log = structlog.get_logger(__name__)
    embedding_cache = FilesystemEmbeddingCache(config.paths.embedding_cache_root)
    extractor = FrozenXLSRExtractor(cache=embedding_cache, backend=_stats_embedding_backend)
    classifier = AASISTClassifier()
    ckpt = _default_checkpoint_path()
    if ckpt.is_file():
        try:
            classifier.load(ckpt)
            log.info("aasist_weights_autoloaded", path=str(ckpt))
        except Exception as exc:
            log.warning("aasist_autoload_failed", path=str(ckpt), error=str(exc))
    calibrator = TemperatureScaler()
    temp_path = ckpt.with_name("temperatures.json")
    if temp_path.is_file():
        try:
            calibrator.load(temp_path)
            log.info("temperatures_autoloaded", path=str(temp_path))
        except Exception as exc:
            log.warning("temperature_autoload_failed", path=str(temp_path), error=str(exc))
    registry = ModelRegistry()
    registry.register(
        "aasist-v1",
        classifier,
        "Acoustic-embedding + AASIST-compatible head (Baseline V1; not frozen XLS-R)",
    )
    return AppContainer(
        config=config,
        audio_loader=SoundFileLoader(),
        audio_validator=MagicByteValidator(max_bytes=config.api.max_upload_bytes),
        preprocessor=DefaultPreprocessor(),
        compressor=FFmpegOpusCompressor(),
        feature_extractor=extractor,
        embedding_cache=embedding_cache,
        classifier=classifier,
        calibrator=calibrator,
        explainer=CompositeExplainer(),
        object_store=LocalObjectStore(config.paths.object_store_root),
        experiment_tracker=FileExperimentTracker(
            root=config.paths.object_store_root / "experiments"
        ),
        human_study_exporter=CsvHumanStudyExporter(),
        model_registry=registry,
    )
