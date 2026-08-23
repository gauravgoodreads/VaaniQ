"""Unit tests for ML pipeline (ROADMAP-029-053)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from vaaniq.calibration import (
    TemperatureScaler,
    brier_score,
    expected_calibration_error,
    predictive_entropy,
    reliability_badge,
)
from vaaniq.config.domains import TrainEnglishOnlyConfig
from vaaniq.core.domain.entities import Embedding, Logits, Waveform
from vaaniq.core.types import CompressionCondition, Label, Language, ReliabilityLevel
from vaaniq.evaluation import (
    EvalReportGenerator,
    classification_report_scores,
    confusion_matrix,
    cross_condition_matrix,
    cross_lingual_matrix,
    equal_error_rate,
    min_dcf,
    pr_curve,
    roc_curve,
)
from vaaniq.explainability import CompositeExplainer, GradCamExplainer
from vaaniq.models import (
    AASISTClassifier,
    LfccGmmClassifier,
    ModelRegistry,
    RawNet2Classifier,
)
from vaaniq.models.baselines.english_only import EnglishOnlyXlsrAasistBaseline
from vaaniq.streaming import StreamingSession, WindowBuffer
from vaaniq.training import FileExperimentTracker, LearningRateScheduler, Trainer


def _emb(dim: int = 1024) -> Embedding:
    rng = np.random.default_rng(0)
    return Embedding(
        vector=rng.normal(0, 1, size=dim).astype(np.float32),
        model_id="xlsr",
        clip_id="c1",
    )


def test_aasist_predict_and_train(tmp_path: Path) -> None:
    clf = AASISTClassifier(input_dim=32, hidden_dim=16, n_blocks=2, rng=np.random.default_rng(0))
    # rebuild with small dim by overriding weights for small input
    clf = AASISTClassifier(rng=np.random.default_rng(0))
    emb = _emb()
    logits = clf.predict(emb)
    assert logits.values.shape == (2,)
    x = np.stack([_emb().vector for _ in range(20)])
    y = np.array([0, 1] * 10, dtype=np.int64)
    loss = clf.train_numpy_epoch(x, y, learning_rate=0.01, batch_size=4)
    assert loss >= 0.0
    ckpt = tmp_path / "a.npz"
    clf.save(ckpt)
    clf2 = AASISTClassifier()
    clf2.load(ckpt)
    assert clf2.predict(emb).values.shape == (2,)


def test_trainer_fit(tmp_path: Path) -> None:
    clf = AASISTClassifier(rng=np.random.default_rng(1))
    tracker = FileExperimentTracker(root=tmp_path, experiment_id="exp1")
    trainer = Trainer(
        clf,
        tracker,
        seed=1,
        max_epochs=3,
        early_stopping_patience=2,
        batch_size=8,
        experiment_root=tmp_path,
    )
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, size=(40, 1024)).astype(np.float32)
    y = np.array([i % 2 for i in range(40)], dtype=np.int64)
    exp_id = trainer.fit(
        {
            "train_features": x,
            "train_labels": y,
            "val_features": x[:8],
            "val_labels": y[:8],
        }
    )
    assert exp_id == "exp1"
    assert (tmp_path / "exp1" / "manifest.json").is_file()


def test_lfcc_gmm_and_rawnet2() -> None:
    sr = 16000
    t = np.arange(sr, dtype=np.float32) / sr
    wav = Waveform(
        samples=(0.1 * np.sin(2 * np.pi * 220 * t)).astype(np.float32), sample_rate_hz=sr
    )
    gmm = LfccGmmClassifier()
    gmm.fit([wav, wav], [Label.REAL, Label.FAKE])
    logits = gmm.predict_waveform(wav)
    assert logits.values.shape == (2,)
    raw = RawNet2Classifier()
    logits2 = raw.predict_waveform(wav)
    assert logits2.values.shape == (2,)
    loss = raw.train_epoch([wav], [Label.REAL], learning_rate=0.01)
    assert loss >= 0.0


def test_registry_and_english_baseline(tmp_path: Path) -> None:
    reg = ModelRegistry()
    assert "aasist-v1" in reg.list_ids()
    assert isinstance(reg.get("aasist-v1"), AASISTClassifier)
    cfg = TrainEnglishOnlyConfig.model_validate(
        {
            "seed": 0,
            "model_config": "model/xlsr_aasist.yaml",
            "audio_preprocessing": "audio/preprocessing.yaml",
            "audio_compression": "audio/compression.yaml",
            "asvspoof_subset": "LA",
            "asvspoof_split": "train",
            "learning_rate": 0.001,
            "batch_size": 8,
            "max_epochs": 2,
            "experiment_root": str(tmp_path),
        }
    )
    baseline = EnglishOnlyXlsrAasistBaseline(cfg)
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, size=(16, 1024)).astype(np.float32)
    y = np.array([i % 2 for i in range(16)], dtype=np.int64)
    result = baseline.run(
        {"train_features": x, "train_labels": y, "val_features": x[:4], "val_labels": y[:4]}
    )
    assert result.experiment_id


def test_metrics_and_matrices(tmp_path: Path) -> None:
    scores = [0.1, 0.2, 0.8, 0.9]
    labels = [0, 0, 1, 1]
    assert 0.0 <= equal_error_rate(scores, labels) <= 1.0
    assert min_dcf(scores, labels) >= 0.0
    report = classification_report_scores(scores, labels)
    assert "f1" in report
    fpr, tpr, auc = roc_curve(scores, labels)
    assert len(fpr) == len(tpr)
    assert 0.0 <= auc <= 1.0
    p, r = pr_curve(scores, labels)
    assert len(p) == len(r)
    assert confusion_matrix(scores, labels)[1][1] >= 0
    xl = cross_lingual_matrix(
        [{"train_lang": "hi", "test_lang": "mr", "scores": scores, "labels": labels}]
    )
    assert xl["hi"]["mr"] >= 0.0
    xc = cross_condition_matrix(
        [
            {
                "train_condition": "clean",
                "test_condition": "opus_whatsapp_sim",
                "scores": scores,
                "labels": labels,
            }
        ]
    )
    assert "clean" in xc
    path = EvalReportGenerator().write("e1", tmp_path / "r.md", metrics=report)
    assert path.is_file()


def test_calibration_and_badge() -> None:
    scaler = TemperatureScaler()
    logits = [Logits(values=np.array([1.0, 0.1], dtype=np.float32)) for _ in range(8)]
    labels = [0] * 4 + [1] * 4
    # mix logits
    logits = [
        Logits(values=np.array([2.0, 0.1], dtype=np.float32)),
        Logits(values=np.array([0.1, 2.0], dtype=np.float32)),
    ] * 4
    labels = [0, 1] * 4
    scaler.fit(logits, labels, language=Language.HI, condition=CompressionCondition.CLEAN)
    probs = scaler.transform(logits[0], language=Language.HI, condition=CompressionCondition.CLEAN)
    assert probs.temperature is not None
    ece = expected_calibration_error([0.9, 0.6, 0.55], [1, 1, 0], n_bins=15)
    assert ece >= 0.0
    assert brier_score([0.8, 0.2], [1, 0]) >= 0.0
    assert predictive_entropy([0.5, 0.5]) > 0.0
    badge = reliability_badge(
        0.6,
        entropy=0.1,
        condition=CompressionCondition.OPUS_WHATSAPP_SIM,
    )
    assert badge == ReliabilityLevel.MODERATE


def test_explain_and_stream(tmp_path: Path) -> None:
    from vaaniq.core.domain.entities import ClipMetadata
    from vaaniq.core.types import DatasetSource, Split

    sr = 16000
    wav = Waveform(
        samples=np.zeros(sr, dtype=np.float32),
        sample_rate_hz=sr,
    )
    clip = ClipMetadata(
        clip_id="c1",
        language=Language.HI,
        source=DatasetSource.TEAM_RECORDING,
        label=Label.REAL,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=sr,
        duration_sec=1.0,
        split=Split.TEST,
        dataset_source="team",
    )
    arts = GradCamExplainer(artefact_root=tmp_path).explain(clip, wav, model_id="aasist-v1")
    assert arts
    arts2 = CompositeExplainer(
        [
            GradCamExplainer(artefact_root=tmp_path),
        ]
    ).explain(clip, wav, model_id="aasist-v1")
    assert arts2
    buf = WindowBuffer(window_sec=0.1, hop_sec=0.05, sample_rate_hz=16000)
    # 0.2s of silence PCM16
    pcm = (np.zeros(int(16000 * 0.25), dtype=np.int16)).tobytes()
    windows = buf.push(pcm)
    assert len(windows) >= 1
    buf.reset()
    session = StreamingSession(session_id="s1", classifier=AASISTClassifier())
    preds = session.ingest(pcm)
    assert isinstance(preds, list)
    assert session.finalize() is not None


def test_scheduler() -> None:
    sch = LearningRateScheduler(0.001, warmup_epochs=2, decay_every=10)
    assert sch.step(0) > 0
    assert sch.step(100) < 0.001


def test_eer_and_min_dcf_are_class_conditional() -> None:
    """Joint rates would report 0.75; class-conditional EER is 1.0 (REQ-046)."""
    scores = [0.5] * 8
    labels = [0, 0, 0, 0, 0, 0, 1, 1]
    eer = equal_error_rate(scores, labels)
    assert eer == pytest.approx(1.0)
    dcf = min_dcf(scores, labels)
    assert dcf > 1.0
