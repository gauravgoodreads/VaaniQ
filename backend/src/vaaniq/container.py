"""Composition root — constructs adapters from config (Phase 1 step 8).

Wires stub implementations today; swap concretes as ROADMAP items land.
No global singletons (vaaniq-core.mdc).
"""

from __future__ import annotations

from dataclasses import dataclass

from vaaniq.audio.compression.ffmpeg_opus import FFmpegOpusCompressor
from vaaniq.audio.io.soundfile_loader import SoundFileLoader
from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.audio.transforms.validator import MagicByteValidator
from vaaniq.calibration.temperature import TemperatureScaler
from vaaniq.config.models import AppConfig
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
from vaaniq.explainability.gradcam import GradCamExplainer
from vaaniq.features.cache.filesystem import FilesystemEmbeddingCache
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor
from vaaniq.human_study.exporter import CsvHumanStudyExporter
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.registry import ModelRegistry
from vaaniq.storage.local import LocalObjectStore
from vaaniq.training.tracker import FileExperimentTracker


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
        AppContainer with Phase-1 stub adapters (ROADMAP bodies deferred).
    """
    return AppContainer(
        config=config,
        audio_loader=SoundFileLoader(),
        audio_validator=MagicByteValidator(),
        preprocessor=DefaultPreprocessor(),
        compressor=FFmpegOpusCompressor(),
        feature_extractor=FrozenXLSRExtractor(),
        embedding_cache=FilesystemEmbeddingCache(),
        classifier=AASISTClassifier(),
        calibrator=TemperatureScaler(),
        explainer=GradCamExplainer(),
        object_store=LocalObjectStore(config.paths.object_store_root),
        experiment_tracker=FileExperimentTracker(),
        human_study_exporter=CsvHumanStudyExporter(),
        model_registry=ModelRegistry(),
    )
