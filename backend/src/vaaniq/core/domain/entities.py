"""Domain value objects and entities.

No FastAPI or SQLAlchemy imports allowed here (vaaniq-core.mdc). ROADMAP-003.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from vaaniq.core.types import (
    AttackType,
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    ReliabilityLevel,
    Split,
)

Float32Array = NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class Waveform:
    """Mono PCM waveform in memory.

    Attributes:
        samples: Float32 samples in ``[-1, 1]`` approximately.
        sample_rate_hz: Sampling rate after decode/preprocess (REQ-098).
    """

    samples: Float32Array
    sample_rate_hz: int

    @property
    def duration_sec(self) -> float:
        """Return duration in seconds."""
        if self.sample_rate_hz <= 0:
            return 0.0
        return float(self.samples.shape[0]) / float(self.sample_rate_hz)


@dataclass(frozen=True, slots=True)
class Embedding:
    """Cached SSL embedding vector or sequence (REQ-036, REQ-037)."""

    vector: Float32Array
    model_id: str
    clip_id: str


@dataclass(frozen=True, slots=True)
class Logits:
    """Raw classifier logits before calibration (REQ-038)."""

    values: Float32Array
    class_order: tuple[Label, ...] = (Label.REAL, Label.FAKE)


@dataclass(frozen=True, slots=True)
class Probabilities:
    """Calibrated class probabilities (REQ-006, REQ-054)."""

    values: Float32Array
    class_order: tuple[Label, ...] = (Label.REAL, Label.FAKE)
    temperature: float | None = None


@dataclass(frozen=True, slots=True)
class ClipMetadata:
    """Per-clip metadata record (REQ-131-133).

    ``speaker_id`` and attack/generation fields are nullable for some sources.
    """

    clip_id: str
    language: Language
    source: DatasetSource
    label: Label
    compression_status: CompressionCondition
    sample_rate_hz: int
    duration_sec: float
    split: Split
    dataset_source: str
    speaker_id: str | None = None
    attack_type: AttackType | None = None
    generation_model: str | None = None
    pair_id: str | None = None
    consent_ref: str | None = None


@dataclass(frozen=True, slots=True)
class UploadBlob:
    """Raw upload awaiting validation (REQ-135)."""

    filename: str
    content_type: str
    data: bytes
    size_bytes: int


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """Inference outcome surfaced to API/UI (REQ-087, REQ-088, REQ-091)."""

    label: Label
    confidence: float
    reliability: ReliabilityLevel
    language: Language
    compression_status: CompressionCondition
    probabilities: Probabilities | None = None


@dataclass(frozen=True, slots=True)
class ExplanationArtefact:
    """Explainability artefact reference (REQ-075-078)."""

    kind: str
    uri: str
    summary: str
    extras: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExperimentManifest:
    """Reproducibility manifest for a run (REQ-137)."""

    experiment_id: str
    git_sha: str
    dirty: bool
    seed: int
    config: Mapping[str, str]
    package_versions: Mapping[str, str]
    hardware: Mapping[str, str]
    dataset_checksums: Mapping[str, str]
