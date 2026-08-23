"""Speaker-disjoint split builder (ROADMAP-017 / REQ-099)."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, replace
from enum import Enum
from pathlib import Path

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import DatasetError
from vaaniq.core.types import Split
from vaaniq.observability.logging import get_logger

log = get_logger(__name__)


def _speaker_bucket(clip: ClipMetadata) -> str:
    """Return the speaker key; orphan clips use ``clip_id`` as their own bucket."""
    if clip.speaker_id is None or not clip.speaker_id.strip():
        return f"clip:{clip.clip_id}"
    return clip.speaker_id


def _clip_to_jsonable(clip: ClipMetadata) -> dict[str, object]:
    """Serialize a clip for JSONL (enums → values)."""
    raw = asdict(clip)
    out: dict[str, object] = {}
    for key, value in raw.items():
        if isinstance(value, Enum):
            out[key] = value.value
        else:
            out[key] = value
    return out


class SpeakerDisjointSplitter:
    """Write versioned speaker-disjoint train/val/test manifests.

    Speakers are assigned to splits; clips follow their speaker (REQ-099).
    Speakers with ``None`` ``speaker_id`` are treated as singleton buckets keyed
    by ``clip_id``. Serves ROADMAP-017.
    """

    def build(
        self,
        clips: Sequence[ClipMetadata],
        *,
        seed: int,
        destination: Path,
        # ASSUMPTION: OQ-008
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Mapping[Split, Path]:
        """Assign speakers to splits and write versioned JSONL manifests.

        Args:
            clips: Input clip metadata (any prior ``split`` is overwritten).
            seed: RNG seed for speaker shuffle.
            destination: Directory that receives ``{train,val,test}.jsonl``.
            train_ratio: Train speaker fraction (ASSUMPTION: OQ-008).
            val_ratio: Val speaker fraction (ASSUMPTION: OQ-008).
            test_ratio: Test speaker fraction (ASSUMPTION: OQ-008).

        Returns:
            Mapping of ``Split`` → written JSONL path.

        Raises:
            DatasetError: If ratios do not sum to ~1.
        """
        total = train_ratio + val_ratio + test_ratio
        if abs(total - 1.0) > 1e-6:
            msg = f"split ratios must sum to 1.0, got {total}"
            raise DatasetError(msg)

        n_orphan = sum(
            1 for clip in clips if clip.speaker_id is None or not clip.speaker_id.strip()
        )
        if n_orphan:
            log.warning(
                "speaker_id_missing_singleton_buckets",
                n_orphan=n_orphan,
                n_clips=len(clips),
            )
        by_speaker: dict[str, list[ClipMetadata]] = defaultdict(list)
        for clip in clips:
            by_speaker[_speaker_bucket(clip)].append(clip)

        speakers = sorted(by_speaker.keys())
        rng = random.Random(seed)
        rng.shuffle(speakers)

        n = len(speakers)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        # Remainder goes to test so all speakers are assigned.
        train_speakers = set(speakers[:n_train])
        val_speakers = set(speakers[n_train : n_train + n_val])
        test_speakers = set(speakers[n_train + n_val :])

        split_for_speaker: dict[str, Split] = {}
        for spk in train_speakers:
            split_for_speaker[spk] = Split.TRAIN
        for spk in val_speakers:
            split_for_speaker[spk] = Split.VAL
        for spk in test_speakers:
            split_for_speaker[spk] = Split.TEST

        buckets: dict[Split, list[ClipMetadata]] = {
            Split.TRAIN: [],
            Split.VAL: [],
            Split.TEST: [],
        }
        for spk, group in by_speaker.items():
            assigned = split_for_speaker[spk]
            for clip in group:
                buckets[assigned].append(replace(clip, split=assigned))

        pair_to_splits: dict[str, set[Split]] = defaultdict(set)
        for split, group in buckets.items():
            for clip in group:
                if clip.pair_id:
                    pair_to_splits[clip.pair_id].add(split)
        leaked = sorted(pid for pid, splits in pair_to_splits.items() if len(splits) > 1)
        if leaked:
            msg = f"clean/compressed pair_id spans splits: {leaked[:20]}"
            raise DatasetError(msg)

        destination.mkdir(parents=True, exist_ok=True)
        paths: dict[Split, Path] = {}
        for split in Split:
            path = destination / f"{split.value}.jsonl"
            with path.open("w", encoding="utf-8") as handle:
                for clip in buckets[split]:
                    handle.write(json.dumps(_clip_to_jsonable(clip), sort_keys=True))
                    handle.write("\n")
            paths[split] = path

        meta_path = destination / "split_version.json"
        meta_path.write_text(
            json.dumps(
                {
                    "seed": seed,
                    # ASSUMPTION: OQ-008
                    "ratios": {
                        "train": train_ratio,
                        "val": val_ratio,
                        "test": test_ratio,
                    },
                    "speaker_counts": {
                        Split.TRAIN.value: len(train_speakers),
                        Split.VAL.value: len(val_speakers),
                        Split.TEST.value: len(test_speakers),
                    },
                    "clip_counts": {split.value: len(buckets[split]) for split in Split},
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        log.info(
            "speaker_disjoint_splits_written",
            destination=str(destination),
            seed=seed,
            n_speakers=n,
            n_clips=len(clips),
        )
        return paths
