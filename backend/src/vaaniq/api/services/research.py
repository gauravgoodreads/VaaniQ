"""In-process human-study + experiment-catalogue service (ROADMAP-059)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from vaaniq.api.schemas.research import HumanResponseIn, ParticipantCreate
from vaaniq.config.domains import HumanStudyProtocolConfig
from vaaniq.container import AppContainer
from vaaniq.core.domain.entities import ClipMetadata
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


def _demo_clips() -> list[ClipMetadata]:
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


@dataclass
class HumanStudyState:
    """Process-local study state."""

    sessions: dict[str, ParticipantSession] = field(default_factory=dict)
    responses: list[dict[str, str]] = field(default_factory=list)
    pool: list[ClipMetadata] = field(default_factory=_demo_clips)


_STATE = HumanStudyState()


class ResearchApiService:
    """Human-study protocol + experiment catalogue for the API."""

    def __init__(self, container: AppContainer) -> None:
        """Bind DI container."""
        self._c = container
        self._protocol = HumanStudyProtocolConfig()
        self._store = ExperimentStore(root=Path("./research/experiments"))

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
        """Human vs model stats on recorded trials (demo model scores from choice)."""
        if not _STATE.responses:
            return {"stats": {}, "n_responses": 0}
        human_pred = [1 if r["choice"] == "fake" else 0 for r in _STATE.responses]
        human_conf = [int(r["confidence_1_5"]) for r in _STATE.responses]
        # Gold labels from demo pool
        gold = {c.clip_id: (0 if c.label.value == "real" else 1) for c in _STATE.pool}
        labels = [gold.get(r["clip_id"], 0) for r in _STATE.responses]
        # Placeholder model scores: slightly shifted human answers (CI-safe)
        model_scores = [min(0.99, max(0.01, p * 0.8 + 0.1)) for p in human_pred]
        stats = human_vs_model_report(
            human_pred=human_pred,
            human_conf_1_5=human_conf,
            human_labels=labels,
            model_scores=model_scores,
            model_labels=labels,
        )
        return {"stats": stats, "n_responses": len(_STATE.responses)}

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
        """Language/label hours for the demo pool (O1 / REQ-034)."""
        stats = DatasetStatistics.compute(_STATE.pool)
        return {
            "total_clips": stats.total_clips,
            "total_hours": stats.total_hours,
            "counts_by_language": {lang.value: n for lang, n in stats.counts_by_language.items()},
            "hours_by_language": {lang.value: h for lang, h in stats.hours_by_language.items()},
            "counts_by_label": {lab.value: n for lab, n in stats.counts_by_label.items()},
            "hours_by_label": {lab.value: h for lab, h in stats.hours_by_label.items()},
            "languages": [lang.value for lang in Language],
            "note": "Demo pool until curated manifests are ingested (OQ-002).",
        }

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
