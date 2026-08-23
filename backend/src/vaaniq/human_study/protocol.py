"""Human-study protocol: registration, balanced assignment (ROADMAP-059 / OQ-011)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

import numpy as np

from vaaniq.config.domains import HumanStudyProtocolConfig
from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import Language


@dataclass
class ParticipantSession:
    """Anonymous volunteer session."""

    participant_id: str
    fluency_self_report: str
    clip_ids: list[str] = field(default_factory=list)


def assign_clips(
    clips: list[ClipMetadata],
    *,
    config: HumanStudyProtocolConfig,
    rng: np.random.Generator | None = None,
) -> list[str]:
    """Shuffle and balance clip IDs across project languages.

    Args:
        clips: Pool of labelled stimuli (no PII).
        config: Protocol YAML.
        rng: Optional generator.

    Returns:
        Ordered clip_id list of length ``clips_per_participant`` (or fewer).
    """
    rng = rng or np.random.default_rng(config.seed)
    per_lang: dict[Language, list[str]] = {lang: [] for lang in Language}
    for clip in clips:
        per_lang[clip.language].append(clip.clip_id)
    for lang in Language:
        ids = per_lang[lang]
        rng.shuffle(ids)
    n = config.clips_per_participant
    n_lang = max(1, len(list(Language)))
    quota = n // n_lang
    chosen: list[str] = []
    for lang in Language:
        chosen.extend(per_lang[lang][:quota])
    leftovers = []
    for lang in Language:
        leftovers.extend(per_lang[lang][quota:])
    rng.shuffle(leftovers)
    chosen.extend(leftovers[: max(0, n - len(chosen))])
    rng.shuffle(chosen)
    return chosen[:n]


def register_participant(fluency_self_report: str) -> ParticipantSession:
    """Create an anonymous participant (UUID only)."""
    return ParticipantSession(
        participant_id=str(uuid.uuid4()),
        fluency_self_report=fluency_self_report,
    )
