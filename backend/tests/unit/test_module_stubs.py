"""Xfail tests for deferred module skeletons (Phase 1 step 8)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from vaaniq.audio import (
    DefaultPreprocessor,
    FallbackDecoderLoader,
    FFmpegOpusCompressor,
    MagicByteValidator,
    SoundFileLoader,
)
from vaaniq.calibration import TemperatureScaler, expected_calibration_error
from vaaniq.core.domain.entities import (
    ClipMetadata,
    Embedding,
    ExperimentManifest,
    Logits,
    UploadBlob,
    Waveform,
)
from vaaniq.core.errors import NotImplementedInPhaseError
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    ExportFormat,
    Label,
    Language,
    Split,
)
from vaaniq.datasets import (
    CommonVoiceSource,
    IndicSynthSource,
    IndicVoicesRSource,
    KathbathSource,
    SpeakerDisjointSplitter,
    TeamRecordingsSource,
    parse_clip_metadata,
)
from vaaniq.evaluation import (
    EvalReportGenerator,
    classification_report_scores,
    cross_condition_matrix,
    cross_lingual_matrix,
    equal_error_rate,
    min_dcf,
)
from vaaniq.explainability import FrequencyBandExplainer, GradCamExplainer
from vaaniq.features import FilesystemEmbeddingCache, FrozenXLSRExtractor
from vaaniq.human_study import CsvHumanStudyExporter
from vaaniq.models import (
    AASISTClassifier,
    LfccGmmClassifier,
    ModelRegistry,
    RawNet2Classifier,
)
from vaaniq.storage import LocalObjectStore
from vaaniq.streaming import StreamingSession, WindowBuffer
from vaaniq.training import (
    FileExperimentTracker,
    LearningRateScheduler,
    Trainer,
    TrainingCallback,
)

_WAV = Waveform(samples=np.zeros(16, dtype=np.float32), sample_rate_hz=16000)
_EMB = Embedding(vector=np.zeros(8, dtype=np.float32), model_id="xlsr", clip_id="c1")
_LOGITS = Logits(values=np.zeros(2, dtype=np.float32))
_CLIP = ClipMetadata(
    clip_id="c1",
    language=Language.HI,
    source=DatasetSource.KATHBATH,
    label=Label.REAL,
    compression_status=CompressionCondition.CLEAN,
    sample_rate_hz=16000,
    duration_sec=1.0,
    split=Split.TRAIN,
    dataset_source="kathbath",
)
_UPLOAD = UploadBlob(
    filename="a.wav",
    content_type="audio/wav",
    data=b"RIFF",
    size_bytes=4,
)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-019", raises=NotImplementedInPhaseError, strict=True)
def test_soundfile_loader() -> None:
    SoundFileLoader().load("missing.wav")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-019", raises=NotImplementedInPhaseError, strict=True)
def test_fallback_loader() -> None:
    FallbackDecoderLoader().load("missing.wav")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-020", raises=NotImplementedInPhaseError, strict=True)
def test_preprocessor() -> None:
    DefaultPreprocessor().transform(_WAV)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-057", raises=NotImplementedInPhaseError, strict=True)
def test_validator() -> None:
    MagicByteValidator().validate(_UPLOAD)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-021", raises=NotImplementedInPhaseError, strict=True)
def test_compressor() -> None:
    FFmpegOpusCompressor().compress(_WAV, {"bitrate": "24k"})


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-025", raises=NotImplementedInPhaseError, strict=True)
def test_xlsr_extractor() -> None:
    FrozenXLSRExtractor().extract(_WAV, clip_id="c1")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-026", raises=NotImplementedInPhaseError, strict=True)
def test_embedding_cache_get() -> None:
    FilesystemEmbeddingCache().get("k")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-029", raises=NotImplementedInPhaseError, strict=True)
def test_aasist() -> None:
    AASISTClassifier().predict(_EMB)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-031", raises=NotImplementedInPhaseError, strict=True)
def test_lfcc_gmm() -> None:
    LfccGmmClassifier().predict(_EMB)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-032", raises=NotImplementedInPhaseError, strict=True)
def test_rawnet2() -> None:
    RawNet2Classifier().predict(_EMB)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-035", raises=NotImplementedInPhaseError, strict=True)
def test_model_registry() -> None:
    ModelRegistry().get("aasist-v1")


@pytest.mark.parametrize(
    "source_cls",
    [
        KathbathSource,
        IndicVoicesRSource,
        CommonVoiceSource,
        IndicSynthSource,
        TeamRecordingsSource,
    ],
)
@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-011", raises=NotImplementedInPhaseError, strict=True)
def test_dataset_sources(source_cls: type) -> None:
    src = source_cls()
    assert src.source_id is not None
    next(iter(src.iter_clips()))


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-017", raises=NotImplementedInPhaseError, strict=True)
def test_splitter(tmp_path: Path) -> None:
    SpeakerDisjointSplitter().build([], seed=42, destination=tmp_path)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-012", raises=NotImplementedInPhaseError, strict=True)
def test_parse_clip_metadata() -> None:
    parse_clip_metadata({})


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-030", raises=NotImplementedInPhaseError, strict=True)
def test_trainer_fit() -> None:
    Trainer(AASISTClassifier(), FileExperimentTracker(), seed=42).fit({})


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-030", raises=NotImplementedInPhaseError, strict=True)
def test_callback() -> None:
    TrainingCallback().on_epoch_end(0, {})


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-030", raises=NotImplementedInPhaseError, strict=True)
def test_scheduler() -> None:
    LearningRateScheduler().step(0)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-030", raises=NotImplementedInPhaseError, strict=True)
def test_tracker_metric() -> None:
    FileExperimentTracker().log_metric("eer", 0.1)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-030", raises=NotImplementedInPhaseError, strict=True)
def test_tracker_manifest() -> None:
    FileExperimentTracker().write_manifest(
        ExperimentManifest(
            experiment_id="e1",
            git_sha="abc",
            dirty=False,
            seed=42,
            config={},
            package_versions={},
            hardware={},
            dataset_checksums={},
        )
    )


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-036", raises=NotImplementedInPhaseError, strict=True)
def test_eer() -> None:
    equal_error_rate([], [])


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-036", raises=NotImplementedInPhaseError, strict=True)
def test_min_dcf() -> None:
    min_dcf([], [])


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-037", raises=NotImplementedInPhaseError, strict=True)
def test_clf_report() -> None:
    classification_report_scores([], [])


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-038", raises=NotImplementedInPhaseError, strict=True)
def test_cross_lingual() -> None:
    cross_lingual_matrix([])


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-039", raises=NotImplementedInPhaseError, strict=True)
def test_cross_condition() -> None:
    cross_condition_matrix([])


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-041", raises=NotImplementedInPhaseError, strict=True)
def test_eval_report(tmp_path: Path) -> None:
    EvalReportGenerator().write("e1", tmp_path / "out.md")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-043", raises=NotImplementedInPhaseError, strict=True)
def test_temperature_fit() -> None:
    TemperatureScaler().fit(
        [],
        [],
        language=Language.HI,
        condition=CompressionCondition.CLEAN,
    )


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-043", raises=NotImplementedInPhaseError, strict=True)
def test_temperature_transform() -> None:
    TemperatureScaler().transform(
        _LOGITS,
        language=Language.HI,
        condition=CompressionCondition.CLEAN,
    )


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-044", raises=NotImplementedInPhaseError, strict=True)
def test_ece() -> None:
    expected_calibration_error([], [], n_bins=10)


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-049", raises=NotImplementedInPhaseError, strict=True)
def test_gradcam() -> None:
    GradCamExplainer().explain(_CLIP, _WAV, model_id="aasist")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-050", raises=NotImplementedInPhaseError, strict=True)
def test_freq_importance() -> None:
    FrequencyBandExplainer().explain(_CLIP, _WAV, model_id="aasist")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-059", raises=NotImplementedInPhaseError, strict=True)
def test_human_export(tmp_path: Path) -> None:
    CsvHumanStudyExporter().export([], fmt=ExportFormat.CSV, destination=tmp_path / "o.csv")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-055", raises=NotImplementedInPhaseError, strict=True)
def test_window_buffer() -> None:
    WindowBuffer().push(b"\x00")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-055", raises=NotImplementedInPhaseError, strict=True)
def test_streaming_session() -> None:
    StreamingSession("s1").ingest(b"\x00")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-009", raises=NotImplementedInPhaseError, strict=True)
def test_local_object_store(tmp_path: Path) -> None:
    LocalObjectStore(tmp_path).put("k", b"data")


@pytest.mark.xfail_roadmap
@pytest.mark.xfail(reason="ROADMAP-026", raises=NotImplementedInPhaseError, strict=True)
def test_embedding_cache_put() -> None:
    FilesystemEmbeddingCache().put("k", _EMB)
