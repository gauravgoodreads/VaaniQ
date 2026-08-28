"""In-process human-study + experiment-catalogue service (ROADMAP-059)."""

from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import HTTPException
from fastapi.responses import FileResponse

from vaaniq.api.schemas.research import HumanResponseIn, ParticipantCreate
from vaaniq.config.domains import HumanStudyProtocolConfig
from vaaniq.container import AppContainer
from vaaniq.core.domain.entities import ClipMetadata, Embedding, Waveform
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    ExportFormat,
    Label,
    Language,
    Split,
)
from vaaniq.datasets.stats.statistics import DatasetStatistics
from vaaniq.human_study.protocol import ParticipantSession, assign_clips, register_participant
from vaaniq.human_study.stats import human_vs_model_report
from vaaniq.research.store import ExperimentStore, collect_hardware

_REPO_ROOT = Path(__file__).resolve().parents[5]
_DEMO_CORPUS_ROOT = _REPO_ROOT / "data" / "demo_corpus"
_PUBLICATION_CORPUS_ROOT = _REPO_ROOT / "data" / "publication_corpus"


def _parse_language(raw: str) -> Language:
    try:
        return Language(raw)
    except ValueError:
        return Language.HI


def _parse_label(raw: str) -> Label:
    try:
        return Label(raw)
    except ValueError:
        return Label.REAL


def _parse_compression(raw: str) -> CompressionCondition:
    try:
        return CompressionCondition(raw)
    except ValueError:
        return CompressionCondition.CLEAN


def _parse_split(raw: str) -> Split:
    try:
        return Split(raw)
    except ValueError:
        return Split.TEST


def _parse_source(raw: str) -> DatasetSource:
    try:
        return DatasetSource(raw)
    except ValueError:
        return DatasetSource.TEAM_RECORDING


def _fallback_demo_clips() -> list[ClipMetadata]:
    clips: list[ClipMetadata] = []
    for lang in Language:
        for k in range(16):
            clips.append(
                ClipMetadata(
                    clip_id=f"{lang.value}-{k}",
                    language=lang,
                    source=DatasetSource.TEAM_RECORDING,
                    label=Label.REAL if k % 2 == 0 else Label.FAKE,
                    compression_status=CompressionCondition.CLEAN
                    if k % 3
                    else CompressionCondition.OPUS_WHATSAPP_SIM,
                    sample_rate_hz=16000,
                    duration_sec=2.0,
                    split=Split.TEST,
                    dataset_source="demo_pool",
                )
            )
    return clips


def _load_demo_clips() -> tuple[list[ClipMetadata], dict[str, Path], str]:
    """Load publication corpus first, then generated demo, then metadata fallback."""
    publication_manifest = _PUBLICATION_CORPUS_ROOT / "manifest.jsonl"
    using_publication = publication_manifest.is_file()
    root = _PUBLICATION_CORPUS_ROOT if using_publication else _DEMO_CORPUS_ROOT
    manifest = root / "manifest.jsonl"
    if not manifest.is_file():
        note = (
            "Metadata demo pool - run scripts/generate_demo_corpus.py "
            "for playable audio (OQ-002)."
        )
        return _fallback_demo_clips(), {}, note

    clips: list[ClipMetadata] = []
    audio_map: dict[str, Path] = {}
    with manifest.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            clip_id = str(row["clip_id"])
            uri = str(row.get("uri", f"audio/{clip_id}.wav"))
            path = root / uri
            clips.append(
                ClipMetadata(
                    clip_id=clip_id,
                    language=_parse_language(str(row.get("language", "hi"))),
                    source=_parse_source(str(row.get("source", "team_recording"))),
                    label=_parse_label(str(row.get("label", "real"))),
                    compression_status=_parse_compression(
                        str(row.get("compression_status", "clean"))
                    ),
                    sample_rate_hz=int(row.get("sample_rate_hz", 16000)),
                    duration_sec=float(row.get("duration_sec", 20.0)),
                    split=_parse_split(str(row.get("split", "test"))),
                    dataset_source=str(row.get("dataset_source", "demo_corpus")),
                    speaker_id=(
                        str(row["speaker_id"]) if row.get("speaker_id") is not None else None
                    ),
                    pair_id=str(row["pair_id"]) if row.get("pair_id") is not None else None,
                    gender=str(row["gender"]) if row.get("gender") is not None else None,
                    checksum_sha256=(
                        str(row["checksum_sha256"])
                        if row.get("checksum_sha256") is not None
                        else None
                    ),
                    uri=uri,
                )
            )
            if path.is_file():
                audio_map[clip_id] = path

    if using_publication:
        note = (
            f"Speaker-disjoint Kathbath + IndicSynth subset "
            f"({len(clips)} playable clean/Opus evaluation instances)."
        )
    else:
        note = (
            f"Local demo corpus ({len(clips)} playable clips under data/demo_corpus). "
            "Synthetic audio for UI / human-study — not curated dissertation hours (OQ-002)."
        )
    return clips, audio_map, note


@dataclass
class HumanStudyState:
    """Process-local study state."""

    sessions: dict[str, ParticipantSession] = field(default_factory=dict)
    responses: list[dict[str, str]] = field(default_factory=list)
    pool: list[ClipMetadata] = field(default_factory=list)
    audio_map: dict[str, Path] = field(default_factory=dict)
    note: str = ""


def _boot_state() -> HumanStudyState:
    pool, audio_map, note = _load_demo_clips()
    return HumanStudyState(pool=pool, audio_map=audio_map, note=note)


_STATE = _boot_state()


class ResearchApiService:
    """Human-study protocol + experiment catalogue for the API."""

    def __init__(self, container: AppContainer) -> None:
        """Bind DI container."""
        self._c = container
        self._protocol = HumanStudyProtocolConfig()
        self._store = ExperimentStore(root=_REPO_ROOT / "research" / "experiments")

    def reload_pool(self) -> None:
        """Reload demo corpus from disk (after generation)."""
        pool, audio_map, note = _load_demo_clips()
        _STATE.pool = pool
        _STATE.audio_map = audio_map
        _STATE.note = note

    def register(self, body: ParticipantCreate) -> ParticipantSession:
        """Register an anonymous volunteer."""
        session = register_participant(body.fluency_self_report)
        session.clip_ids = assign_clips(_STATE.pool, config=self._protocol)
        _STATE.sessions[session.participant_id] = session
        return session

    def record(self, body: HumanResponseIn) -> dict[str, str]:
        """Store one anonymised response."""
        if body.participant_id not in _STATE.sessions:
            session = register_participant("unknown")
            session.participant_id = body.participant_id
            _STATE.sessions[body.participant_id] = session
        row = {
            "participant_id": body.participant_id,
            "clip_id": body.clip_id,
            "choice": body.choice,
            "confidence_1_5": str(body.confidence_1_5),
            "response_ms": str(body.response_ms),
            "language": body.language,
            "compression_status": body.compression_status,
        }
        _STATE.responses.append(row)
        return row

    def export(self, destination: Path, fmt: ExportFormat = ExportFormat.CSV) -> Path:
        """Export anonymised CSV/JSON."""
        return self._c.human_study_exporter.export(
            _STATE.responses, fmt=fmt, destination=destination
        )

    def comparison_report(self) -> dict[str, object]:
        """Human vs model stats using real classifier scores on study clips."""
        if not _STATE.responses:
            return {
                "stats": {},
                "n_responses": 0,
                "note": "Human-study protocol ready; participant data collection pending (N=0).",
            }
        human_pred = [1 if r["choice"] == "fake" else 0 for r in _STATE.responses]
        human_conf = [int(r["confidence_1_5"]) for r in _STATE.responses]
        gold = {c.clip_id: (0 if c.label.value == "real" else 1) for c in _STATE.pool}
        labels = [gold.get(r["clip_id"], 0) for r in _STATE.responses]
        model_scores: list[float] = []
        classifier = self._c.model_registry.get("aasist-v1")
        pre = self._c.preprocessor
        for response in _STATE.responses:
            clip_id = str(response["clip_id"])
            path = _STATE.audio_map.get(clip_id)
            if path is None or not path.is_file():
                model_scores.append(0.5)
                continue
            data, sr = sf.read(str(path), dtype="float32", always_2d=False)
            if getattr(data, "ndim", 1) > 1:
                data = np.mean(data, axis=1)
            wav = pre.transform(
                Waveform(samples=np.asarray(data, dtype=np.float32), sample_rate_hz=int(sr))
            )
            try:
                emb = self._c.feature_extractor.extract(wav, clip_id=clip_id)
            except Exception:
                vec = np.zeros(1024, dtype=np.float32)
                flat = np.asarray(wav.samples, dtype=np.float32).reshape(-1)
                n = min(vec.size, flat.size)
                vec[:n] = flat[:n]
                emb = Embedding(vector=vec, model_id="fallback", clip_id=clip_id)
            clip_meta = next((c for c in _STATE.pool if c.clip_id == clip_id), None)
            lang = clip_meta.language if clip_meta else Language.HI
            cond = clip_meta.compression_status if clip_meta else CompressionCondition.CLEAN
            logits = classifier.predict(emb)
            probs = self._c.calibrator.transform(logits, language=lang, condition=cond)
            fake_idx = list(probs.class_order).index(Label.FAKE)
            model_scores.append(float(probs.values[fake_idx]))
        stats = human_vs_model_report(
            human_pred=human_pred,
            human_conf_1_5=human_conf,
            human_labels=labels,
            model_scores=model_scores,
            model_labels=labels,
        )
        return {
            "stats": stats,
            "n_responses": len(_STATE.responses),
            "note": "Model scores from loaded aasist-v1 checkpoint on identical study clips.",
        }

    def compare_experiments(self, metric: str = "eer") -> list[dict[str, object]]:
        """Experiment comparison rows."""
        return self._store.compare(metric)

    def hardware(self) -> dict[str, str]:
        """Monitoring hook."""
        return collect_hardware()

    def git_sha(self) -> str:
        """Resolved git SHA for monitoring."""
        return self._store.git_sha()

    def dataset_explorer(self) -> dict[str, object]:
        """Language/label hours for the active clip pool (O1 / REQ-034)."""
        if not _STATE.pool:
            self.reload_pool()
        stats = DatasetStatistics.compute(_STATE.pool)
        samples = [
            {
                "clip_id": c.clip_id,
                "language": c.language.value,
                "label": c.label.value,
                "compression_status": c.compression_status.value,
                "duration_sec": c.duration_sec,
                "has_audio": c.clip_id in _STATE.audio_map,
            }
            for c in _STATE.pool[:24]
        ]
        return {
            "total_clips": stats.total_clips,
            "total_hours": stats.total_hours,
            "counts_by_language": {lang.value: n for lang, n in stats.counts_by_language.items()},
            "hours_by_language": {lang.value: h for lang, h in stats.hours_by_language.items()},
            "counts_by_label": {lab.value: n for lab, n in stats.counts_by_label.items()},
            "hours_by_label": {lab.value: h for lab, h in stats.hours_by_label.items()},
            "languages": [lang.value for lang in Language],
            "note": _STATE.note,
            "playable_clips": len(_STATE.audio_map),
            "samples": samples,
        }

    def clip_audio(self, clip_id: str) -> FileResponse:
        """Serve a demo corpus WAV for explorer / human study."""
        path = _STATE.audio_map.get(clip_id)
        if path is None or not path.is_file():
            raise HTTPException(status_code=404, detail=f"audio not found for clip_id={clip_id}")
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return FileResponse(path, media_type=media_type, filename=path.name)

    def clip_meta(self, clip_id: str) -> dict[str, object]:
        """Metadata for one study / explorer clip."""
        for c in _STATE.pool:
            if c.clip_id == clip_id:
                return {
                    "clip_id": c.clip_id,
                    "language": c.language.value,
                    "label": c.label.value,
                    "compression_status": c.compression_status.value,
                    "duration_sec": c.duration_sec,
                    "has_audio": clip_id in _STATE.audio_map,
                }
        raise HTTPException(status_code=404, detail=f"unknown clip_id={clip_id}")

    def search_experiments(
        self,
        *,
        language: str | None = None,
        model_version: str | None = None,
        rq_id: str | None = None,
    ) -> list[dict[str, object]]:
        """Search the research catalogue."""
        recs = self._store.search(language=language, model_version=model_version, rq_id=rq_id)
        return [rec.to_dict() for rec in recs]
