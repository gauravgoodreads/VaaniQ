"""Research experiment records (ROADMAP-030 extension / RQ1-RQ5)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ResearchRunRecord:
    """Searchable experiment record for the research store.

    Serves REQ-137-138. Fields map to Phase-4 experiment framework.
    """

    experiment_id: str
    timestamp: str
    git_sha: str
    model_version: str
    dataset_version: str
    languages: tuple[str, ...]
    compression_settings: str
    hyperparameters: dict[str, str]
    metrics: dict[str, float]
    calibration_results: dict[str, float]
    hardware: dict[str, str]
    seed: int
    training_duration_sec: float
    rq_ids: tuple[str, ...] = ()
    notes: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL."""
        payload = asdict(self)
        payload["languages"] = list(self.languages)
        payload["rq_ids"] = list(self.rq_ids)
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ResearchRunRecord:
        """Deserialize a JSON object."""
        return cls(
            experiment_id=str(raw["experiment_id"]),
            timestamp=str(raw["timestamp"]),
            git_sha=str(raw["git_sha"]),
            model_version=str(raw["model_version"]),
            dataset_version=str(raw["dataset_version"]),
            languages=tuple(str(x) for x in raw.get("languages", ())),
            compression_settings=str(raw.get("compression_settings", "")),
            hyperparameters={
                str(k): str(v) for k, v in dict(raw.get("hyperparameters", {})).items()
            },
            metrics={str(k): float(v) for k, v in dict(raw.get("metrics", {})).items()},
            calibration_results={
                str(k): float(v) for k, v in dict(raw.get("calibration_results", {})).items()
            },
            hardware={str(k): str(v) for k, v in dict(raw.get("hardware", {})).items()},
            seed=int(raw.get("seed", 42)),
            training_duration_sec=float(raw.get("training_duration_sec", 0.0)),
            rq_ids=tuple(str(x) for x in raw.get("rq_ids", ())),
            notes=str(raw.get("notes", "")),
            extras=dict(raw.get("extras", {})),
        )
