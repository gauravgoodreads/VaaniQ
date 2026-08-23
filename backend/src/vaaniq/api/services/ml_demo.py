"""In-process ML demo service for API routes (ROADMAP-054+).

Uses DI container ports; stores history in memory for the demo process.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import soundfile as sf
import structlog

from vaaniq.api.schemas.ml import (
    CalibrationResponse,
    ExplainResponse,
    HistoryItem,
    PredictionResponse,
    UploadResponse,
)
from vaaniq.audio.transforms.spectrogram import stft_magnitude
from vaaniq.calibration.ece import (
    brier_score,
    coverage_accuracy_curve,
    expected_calibration_error,
    predictive_entropy,
    reliability_badge,
    reliability_diagram,
)
from vaaniq.container import AppContainer
from vaaniq.core.domain.entities import (
    ClipMetadata,
    Embedding,
    UploadBlob,
    Waveform,
)
from vaaniq.core.errors import ValidationError
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    Label,
    Language,
    Split,
)
from vaaniq.evaluation import (
    EvalReportGenerator,
    classification_report_scores,
    confusion_matrix,
    cross_condition_matrix,
    cross_lingual_matrix,
    equal_error_rate,
    min_dcf,
    per_attack_report,
    per_language_report,
)
from vaaniq.streaming.session import StreamingSession

log = structlog.get_logger(__name__)


@dataclass
class MlDemoState:
    """Process-local history / uploads / live sessions."""

    history: list[HistoryItem] = field(default_factory=list)
    uploads: dict[str, Path] = field(default_factory=dict)
    predictions: dict[str, PredictionResponse] = field(default_factory=dict)
    sessions: dict[str, StreamingSession] = field(default_factory=dict)
    last_report: str = ""


_STATE = MlDemoState()


class MlApiService:
    """Orchestrate upload → preprocess → embed → classify → calibrate → explain."""

    def __init__(self, container: AppContainer) -> None:
        """Bind composition root."""
        self._c = container

    def upload(self, filename: str, content_type: str, data: bytes) -> UploadResponse:
        """Validate and store upload bytes."""
        blob = UploadBlob(
            filename=filename,
            content_type=content_type,
            data=data,
            size_bytes=len(data),
        )
        self._c.audio_validator.validate(blob)
        upload_id = str(uuid.uuid4())
        key = f"uploads/{upload_id}"
        uri = self._c.object_store.put(key, data, content_type=content_type)
        dest = Path(uri)
        _STATE.uploads[upload_id] = dest
        log.info("upload_stored", upload_id=upload_id, size=len(data), key=key)
        return UploadResponse(
            upload_id=upload_id,
            filename=filename,
            size_bytes=len(data),
            content_type=content_type,
        )

    def infer_upload(
        self,
        upload_id: str,
        *,
        language: Language = Language.HI,
        model_id: str = "aasist-v1",
    ) -> PredictionResponse:
        """Run full inference on a stored upload."""
        path = _STATE.uploads.get(upload_id)
        if path is None or not path.is_file():
            raise ValidationError(f"unknown upload_id={upload_id}")
        wav = self._c.audio_loader.load(path)
        duration = float(wav.samples.size) / float(max(wav.sample_rate_hz, 1))
        if duration > float(self._c.config.api.max_audio_duration_sec):
            raise ValidationError("audio duration exceeds maximum")
        wav = self._c.preprocessor.transform(wav)
        return self._predict_waveform(
            wav, language=language, model_id=model_id, source_name=path.name
        )

    def infer_bytes(
        self,
        data: bytes,
        *,
        filename: str = "clip.wav",
        content_type: str = "audio/wav",
        language: Language = Language.HI,
        model_id: str = "aasist-v1",
    ) -> PredictionResponse:
        """Upload+infer convenience for multipart endpoints."""
        up = self.upload(filename, content_type, data)
        return self.infer_upload(up.upload_id, language=language, model_id=model_id)

    def _predict_waveform(
        self,
        wav: Waveform,
        *,
        language: Language,
        model_id: str,
        source_name: str,
    ) -> PredictionResponse:
        clip_id = str(uuid.uuid4())
        classifier = self._c.model_registry.get(model_id)
        # Build embedding via feature extractor when possible; else pad vector
        try:
            emb = self._c.feature_extractor.extract(wav, clip_id=clip_id)
        except Exception:
            log.warning("embedding_extract_failed", clip_id=clip_id, model_id=model_id)
            dim = getattr(classifier, "input_dim", 1024)
            vec = np.zeros(int(dim), dtype=np.float32)
            flat = np.asarray(wav.samples, dtype=np.float32).reshape(-1)
            n = min(vec.size, flat.size)
            vec[:n] = flat[:n]
            emb = Embedding(vector=vec, model_id="fallback", clip_id=clip_id)

        logits = classifier.predict(emb)
        condition = CompressionCondition.CLEAN
        probs = self._c.calibrator.transform(logits, language=language, condition=condition)
        fake_idx = list(probs.class_order).index(Label.FAKE)
        fake_p = float(probs.values[fake_idx])
        label = Label.FAKE if fake_p >= 0.5 else Label.REAL
        confidence = max(fake_p, 1.0 - fake_p)
        entropy = predictive_entropy(probs.values.tolist())
        badge = reliability_badge(confidence, entropy=entropy, condition=condition)

        # Waveform / spectrogram previews (downsampled)
        wave_preview = wav.samples[:: max(1, wav.samples.size // 256)].astype(float).tolist()
        spec = stft_magnitude(wav.samples)
        spec_small = spec[::8, :: max(1, spec.shape[1] // 64)].astype(float).tolist()

        pred_id = str(uuid.uuid4())
        resp = PredictionResponse(
            prediction_id=pred_id,
            label=label.value,
            confidence=confidence,
            reliability=badge.value,
            language=language.value,
            compression_status=condition.value,
            probabilities={
                c.value: float(p) for c, p in zip(probs.class_order, probs.values, strict=True)
            },
            waveform=wave_preview,
            spectrogram=spec_small,
        )
        _STATE.predictions[pred_id] = resp
        _STATE.history.insert(
            0,
            HistoryItem(
                prediction_id=pred_id,
                label=resp.label,
                confidence=resp.confidence,
                reliability=resp.reliability,
                language=resp.language,
                created_at=datetime.now(UTC).isoformat(),
            ),
        )
        # Explain artefacts
        clip = ClipMetadata(
            clip_id=clip_id,
            language=language,
            source=DatasetSource.TEAM_RECORDING,
            label=label,
            compression_status=condition,
            sample_rate_hz=wav.sample_rate_hz,
            duration_sec=wav.duration_sec,
            split=Split.TEST,
            dataset_source=source_name,
        )
        self._c.explainer.explain(clip, wav, model_id=model_id)
        log.info("inference_complete", prediction_id=pred_id, label=label.value)
        return resp

    def history(self) -> list[HistoryItem]:
        """Return prediction history."""
        return list(_STATE.history)

    def experiments(self) -> list[dict[str, str]]:
        """List experiment directories."""
        root = Path("./research/experiments")
        if not root.is_dir():
            return []
        return [
            {"experiment_id": p.name, "path": str(p)} for p in sorted(root.iterdir()) if p.is_dir()
        ]

    def metrics_snapshot(self) -> dict[str, object]:
        """Demo metrics from in-memory history scores."""
        if not _STATE.history:
            scores = [0.1, 0.8, 0.2, 0.9]
            labels = [0, 1, 0, 1]
        else:
            scores = [
                h.confidence if h.label == "fake" else 1.0 - h.confidence for h in _STATE.history
            ]
            labels = [1 if h.label == "fake" else 0 for h in _STATE.history]
        metrics = {
            "eer": equal_error_rate(scores, labels),
            "min_dcf": min_dcf(scores, labels),
            **classification_report_scores(scores, labels),
            "confusion": confusion_matrix(scores, labels),
        }
        matrices = {
            "cross_lingual": cross_lingual_matrix(
                [
                    {
                        "train_lang": "hi",
                        "test_lang": "hi",
                        "scores": scores,
                        "labels": labels,
                    }
                ]
            ),
            "cross_condition": cross_condition_matrix(
                [
                    {
                        "train_condition": "clean",
                        "test_condition": "clean",
                        "scores": scores,
                        "labels": labels,
                    }
                ]
            ),
        }
        slices = {
            "language": per_language_report(
                [{"language": "hi", "scores": scores, "labels": labels}]
            ),
            "attack": per_attack_report(
                [{"attack_type": "tts", "scores": scores, "labels": labels}]
            ),
        }
        return {"metrics": metrics, "matrices": matrices, "slices": slices}

    def calibration_snapshot(self) -> CalibrationResponse:
        """Demo calibration summary."""
        conf = [h.confidence for h in _STATE.history] or [0.6, 0.9, 0.55, 0.8]
        correct = [1 if h.label == "fake" else 0 for h in _STATE.history] or [1, 1, 0, 1]
        # treat correct as binary correctness proxy in demo
        corr = [1 if c >= 0.5 else 0 for c in conf]
        return CalibrationResponse(
            ece=expected_calibration_error(conf, corr),
            brier=brier_score(conf, correct),
            reliability_diagram=reliability_diagram(conf, corr),
            coverage_curve=coverage_accuracy_curve(conf, corr),
            temperatures={"hi|clean": 1.0, "mr|clean": 1.0, "ta|clean": 1.0},
        )

    def explain_last(self, prediction_id: str | None = None) -> ExplainResponse:
        """Return explain artefact URIs for a prediction (best-effort scan)."""
        root = Path("./research/explain")
        arts: list[dict[str, str]] = []
        if root.is_dir():
            for p in sorted(root.glob("*.json"))[-8:]:
                arts.append({"kind": p.stem.split("_")[-1], "uri": str(p), "summary": p.name})
        if prediction_id:
            arts = [a for a in arts if prediction_id[:8] in a["uri"]] or arts
        return ExplainResponse(artefacts=arts)

    def live_start(self, session_id: str | None = None) -> str:
        """Create a live session."""
        sid = session_id or str(uuid.uuid4())
        _STATE.sessions[sid] = StreamingSession(
            session_id=sid,
            classifier=self._c.classifier,
        )
        return sid

    def live_ingest(self, session_id: str, chunk: bytes) -> list[PredictionResponse]:
        """Ingest PCM chunk."""
        session = _STATE.sessions.get(session_id)
        if session is None:
            self.live_start(session_id)
            session = _STATE.sessions[session_id]
        preds = session.ingest(chunk)
        out: list[PredictionResponse] = []
        for p in preds:
            out.append(
                PredictionResponse(
                    prediction_id=str(uuid.uuid4()),
                    label=p.label.value,
                    confidence=p.confidence,
                    reliability=p.reliability.value,
                    language=p.language.value,
                    compression_status=p.compression_status.value,
                    probabilities={
                        c.value: float(v)
                        for c, v in zip(
                            p.probabilities.class_order
                            if p.probabilities
                            else (Label.REAL, Label.FAKE),
                            p.probabilities.values if p.probabilities else np.array([0.5, 0.5]),
                            strict=True,
                        )
                    },
                )
            )
        return out

    def write_report(self, experiment_id: str = "demo") -> str:
        """Generate downloadable markdown report."""
        snap = self.metrics_snapshot()
        dest = Path("./research/experiments/reports") / f"{experiment_id}.md"
        EvalReportGenerator().write(
            experiment_id,
            dest,
            metrics=snap["metrics"],  # type: ignore[arg-type]
            matrices=snap["matrices"],  # type: ignore[arg-type]
            slices=snap["slices"],  # type: ignore[arg-type]
        )
        text = dest.read_text(encoding="utf-8")
        _STATE.last_report = text
        return text


def write_sine_wav(path: Path, *, seconds: float = 0.5, sr: int = 16000) -> None:
    """Helper for tests: write a short sine wav."""
    t = np.arange(int(sr * seconds), dtype=np.float32) / float(sr)
    y = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), y, sr)
