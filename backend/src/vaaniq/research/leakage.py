"""Leakage and data-quality audit for research manifests (Phase 6 / REQ-099)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.errors import DatasetError
from vaaniq.core.types import CompressionCondition, Language, Split
from vaaniq.datasets.validators.gates import require_fields


def _speaker_bucket(clip: ClipMetadata) -> str:
    """Speaker key; missing ids become per-clip buckets."""
    if clip.speaker_id is None or not clip.speaker_id.strip():
        return f"clip:{clip.clip_id}"
    return clip.speaker_id


def audit_manifest(
    clips: Sequence[ClipMetadata],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Return structured findings. Does not invent hours or metric scores.

    Args:
        clips: Parsed clip metadata.
        repo_root: Optional root used to resolve ``clip.uri`` existence.

    Returns:
        Audit payload with counts, blocking issues, and warnings.
    """
    blocking: list[str] = []
    warnings: list[str] = []
    require_ok = 0
    for clip in clips:
        try:
            require_fields(clip)
            require_ok += 1
        except DatasetError as exc:
            blocking.append(f"{clip.clip_id}: {exc}")

    ids = [c.clip_id for c in clips]
    dup_ids = sorted({i for i in ids if ids.count(i) > 1})
    if dup_ids:
        blocking.append(f"duplicate_clip_id={dup_ids}")

    langs = {c.language for c in clips}
    if Language.TA not in langs:
        blocking.append("tamil_language_code_absent_from_manifest")
    extra = langs - set(Language)
    if extra:
        blocking.append(f"unexpected_language={sorted(x.value for x in extra)}")

    missing_audio = 0
    if repo_root is not None:
        for clip in clips:
            if not clip.uri:
                missing_audio += 1
                continue
            path = Path(clip.uri)
            if not path.is_absolute():
                path = repo_root / clip.uri
            if not path.is_file():
                missing_audio += 1
    if missing_audio:
        blocking.append(f"audio_bytes_missing_for_n={missing_audio}")

    n_orphan = sum(1 for c in clips if c.speaker_id is None or not c.speaker_id.strip())
    if n_orphan:
        warnings.append(f"speaker_id_missing_n={n_orphan}")

    speakers_by_split: dict[str, set[Split]] = defaultdict(set)
    for clip in clips:
        speakers_by_split[_speaker_bucket(clip)].add(clip.split)
    leak = sorted(spk for spk, splits in speakers_by_split.items() if len(splits) > 1)
    if leak:
        blocking.append(f"speaker_split_leakage={leak[:20]}")

    pair_splits: dict[str, set[Split]] = defaultdict(set)
    pair_conditions: dict[str, set[CompressionCondition]] = defaultdict(set)
    for clip in clips:
        if clip.pair_id:
            pair_splits[clip.pair_id].add(clip.split)
            pair_conditions[clip.pair_id].add(clip.compression_status)
    pair_leak = sorted(pid for pid, splits in pair_splits.items() if len(splits) > 1)
    if pair_leak:
        blocking.append(f"pair_split_leakage={pair_leak[:20]}")

    split_counts = {s.value: sum(1 for c in clips if c.split == s) for s in Split}
    if clips and split_counts.get("val", 0) == 0:
        warnings.append("no_validation_split_rows")
    if clips and split_counts.get("test", 0) == 0:
        warnings.append("no_test_split_rows")

    n_checksum = sum(1 for c in clips if c.checksum_sha256)
    if clips and n_checksum < len(clips):
        warnings.append(f"checksum_missing_n={len(clips) - n_checksum}")

    uris = [c.uri for c in clips if c.uri]
    dup_uris = sorted({u for u in uris if uris.count(u) > 1})
    if dup_uris:
        blocking.append(f"duplicate_uri={dup_uris[:20]}")

    checksums = [c.checksum_sha256 for c in clips if c.checksum_sha256]
    dup_cs = sorted({c for c in checksums if checksums.count(c) > 1})
    if dup_cs:
        blocking.append(f"duplicate_checksum={dup_cs[:20]}")

    return {
        "n_clips": len(clips),
        "n_require_ok": require_ok,
        "n_orphan_speakers": n_orphan,
        "n_missing_audio_bytes": missing_audio,
        "languages": sorted(lang.value for lang in langs),
        "tamil_in_manifest": Language.TA in langs,
        "tamil_audio_verified": Language.TA in langs and missing_audio == 0 and len(clips) > 0,
        "split_counts": split_counts,
        "blocking": blocking,
        "warnings": warnings,
        "can_train": len(clips) > 0 and not blocking,
    }
