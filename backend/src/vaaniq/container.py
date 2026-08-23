"""Composition root — constructs adapters from config (Phase 1 step 8).

No global singletons (vaaniq-core.mdc).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

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
from vaaniq.features.cache.filesystem import FilesystemEmbeddingCache
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor
from vaaniq.human_study.exporter import CsvHumanStudyExporter
from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.registry import ModelRegistry
from vaaniq.storage.local import LocalObjectStore
from vaaniq.training.tracker import FileExperimentTracker


def _stats_embedding_backend(wav: Waveform) -> np.ndarray:
    """Deterministic demo embedding without HF weights (CI / local).

    Produces a 1024-D vector from waveform moments so AASIST can run offline.
    """
    samples = np.asarray(wav.samples, dtype=np.float32).reshape(-1)
    dim = 1024
    vec = np.zeros(dim, dtype=np.float32)
    if samples.size == 0:
        return vec
    stats = np.array(
        [
            float(np.mean(samples)),
            float(np.std(samples)),
            float(np.max(samples)),
            float(np.min(samples)),
            float(np.mean(np.abs(samples))),
            float(np.mean(np.square(samples))),
        ],
        dtype=np.float32,
    )
    vec[: stats.size] = stats
    n_fft = min(512, samples.size)
    spec = np.abs(np.fft.rfft(samples[:n_fft]))
    n = min(dim - 16, spec.size)
    vec[16 : 16 + n] = spec[:n].astype(np.float32)
    return vec


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
    embedding_cache = FilesystemEmbeddingCache(config.paths.embedding_cache_root)
    extractor = FrozenXLSRExtractor(cache=embedding_cache, backend=_stats_embedding_backend)
    classifier = AASISTClassifier()
    registry = ModelRegistry()
    registry.register("aasist-v1", classifier, "Primary XLS-R + AASIST head (REQ-038)")
    return AppContainer(
        config=config,
        audio_loader=SoundFileLoader(),
        audio_validator=MagicByteValidator(max_bytes=config.api.max_upload_bytes),
        preprocessor=DefaultPreprocessor(),
        compressor=FFmpegOpusCompressor(),
        feature_extractor=extractor,
        embedding_cache=embedding_cache,
        classifier=classifier,
        calibrator=TemperatureScaler(),
        explainer=CompositeExplainer(),
        object_store=LocalObjectStore(config.paths.object_store_root),
        experiment_tracker=FileExperimentTracker(
            root=config.paths.object_store_root / "experiments"
        ),
        human_study_exporter=CsvHumanStudyExporter(),
        model_registry=registry,
    )
