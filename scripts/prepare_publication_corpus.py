#!/usr/bin/env python3
"""Prepare a reproducible Kathbath + IndicSynth publication subset.

The script streams gated Kathbath bonafide speech and public IndicSynth
generated speech for Hindi, Marathi, and Tamil. Audio is normalized to
16 kHz mono FLAC, speakers are assigned deterministically to disjoint
train/validation/test splits, and complete provenance is persisted.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import soundfile as sf

LANGUAGES: dict[str, tuple[str, str]] = {
    "hi": ("hindi", "Hindi"),
    "mr": ("marathi", "Marathi"),
    "ta": ("tamil", "Tamil"),
}
KATHBATH_REPO = "ai4bharat/Kathbath"
INDICSYNTH_REPO = "vdivyasharma/IndicSynth"


def speaker_split(speaker_id: str, *, seed: int) -> str:
    """Return a deterministic 70/15/15 speaker-disjoint split."""
    digest = hashlib.sha256(f"{seed}:{speaker_id}".encode()).digest()
    bucket = int.from_bytes(digest[:4], "big") % 10_000
    if bucket < 7_000:
        return "train"
    if bucket < 8_500:
        return "val"
    return "test"


def resample_mono(
    samples: np.ndarray,
    source_rate: int,
    *,
    target_rate: int,
    max_duration_sec: float,
) -> np.ndarray:
    """Convert decoded audio to normalized mono float32 at the target rate."""
    audio = np.asarray(samples, dtype=np.float32)
    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)
    if audio.ndim != 1:
        msg = f"expected mono/stereo audio, got shape {audio.shape}"
        raise ValueError(msg)
    if source_rate <= 0 or target_rate <= 0:
        raise ValueError("sample rates must be positive")
    if source_rate != target_rate:
        target_length = max(1, round(audio.size * target_rate / source_rate))
        source_x = np.linspace(0.0, 1.0, audio.size, endpoint=False)
        target_x = np.linspace(0.0, 1.0, target_length, endpoint=False)
        audio = np.interp(target_x, source_x, audio).astype(np.float32)
    max_samples = int(target_rate * max_duration_sec)
    audio = audio[:max_samples]
    if audio.size == 0:
        raise ValueError("decoded audio is empty")
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio * np.float32(0.95 / peak)
    return audio.astype(np.float32)


def _audio_bytes(value: object) -> bytes:
    if not isinstance(value, Mapping):
        raise ValueError("audio field is not a mapping")
    payload = value.get("bytes")
    if not isinstance(payload, bytes) or not payload:
        raise ValueError("audio bytes are unavailable")
    return payload


def _decode(value: object) -> tuple[np.ndarray, int]:
    samples, sample_rate = sf.read(
        io.BytesIO(_audio_bytes(value)),
        dtype="float32",
        always_2d=False,
    )
    return np.asarray(samples, dtype=np.float32), int(sample_rate)


def _stream_rows(
    repo_id: str,
    config: str,
    *,
    audio_column: str,
    token: str | None,
    seed: int,
    shuffle_buffer: int,
) -> Iterable[Mapping[str, object]]:
    from datasets import Audio, load_dataset

    dataset = load_dataset(
        repo_id,
        config,
        split="train",
        streaming=True,
        token=token,
    )
    dataset = dataset.cast_column(audio_column, Audio(decode=False))
    dataset = dataset.shuffle(seed=seed, buffer_size=shuffle_buffer)
    yield from dataset


def _safe_int(value: object) -> int:
    if isinstance(value, int | float):
        return int(value)
    return int(str(value))


def _write_sample(
    *,
    row: Mapping[str, object],
    root: Path,
    language: str,
    label: str,
    source: str,
    audio_column: str,
    source_name: str,
    speaker_value: object,
    generation_model: str | None,
    gender: str | None,
    index: int,
    seed: int,
    target_rate: int,
    max_duration_sec: float,
) -> dict[str, object]:
    speaker_id = f"spk-{_safe_int(speaker_value)}"
    raw_samples, source_rate = _decode(row[audio_column])
    samples = resample_mono(
        raw_samples,
        source_rate,
        target_rate=target_rate,
        max_duration_sec=max_duration_sec,
    )
    if samples.size < target_rate:
        raise ValueError("clip is shorter than one second")
    identity = f"{source}:{language}:{speaker_id}:{index}"
    clip_hash = hashlib.sha256(identity.encode()).hexdigest()[:16]
    clip_id = f"{language}-{label}-{clip_hash}"
    relative = Path("audio") / language / label / f"{clip_id}.flac"
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, samples, target_rate, format="FLAC")
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    return {
        "clip_id": clip_id,
        "language": language,
        "label": label,
        "compression_status": "clean",
        "sample_rate_hz": target_rate,
        "duration_sec": round(samples.size / target_rate, 4),
        "split": speaker_split(speaker_id, seed=seed),
        "dataset_source": source_name,
        "source": source,
        "speaker_id": speaker_id,
        "attack_type": "voice_clone" if label == "fake" else None,
        "generation_model": generation_model,
        "gender": gender,
        "checksum_sha256": checksum,
        "uri": relative.as_posix(),
    }


def _collect_cell(
    *,
    rows: Iterable[Mapping[str, object]],
    root: Path,
    language: str,
    label: str,
    source: str,
    audio_column: str,
    source_name: str,
    speaker_key: str,
    model_key: str | None,
    gender_key: str,
    target_count: int,
    seed: int,
    target_rate: int,
    max_duration_sec: float,
) -> list[dict[str, object]]:
    collected: list[dict[str, object]] = []
    failures = 0
    for index, row in enumerate(rows):
        if len(collected) >= target_count:
            break
        try:
            model_value = row.get(model_key) if model_key is not None else None
            record = _write_sample(
                row=row,
                root=root,
                language=language,
                label=label,
                source=source,
                audio_column=audio_column,
                source_name=source_name,
                speaker_value=row[speaker_key],
                generation_model=str(model_value) if model_value is not None else None,
                gender=str(row.get(gender_key)) if row.get(gender_key) is not None else None,
                index=index,
                seed=seed,
                target_rate=target_rate,
                max_duration_sec=max_duration_sec,
            )
        except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
            failures += 1
            if failures <= 5:
                print(f"skip {source_name}/{language} row {index}: {exc}")
            continue
        collected.append(record)
        if len(collected) % 50 == 0:
            print(f"{source_name}/{language}: {len(collected)}/{target_count}")
    if len(collected) != target_count:
        msg = (
            f"{source_name}/{language}: requested {target_count}, "
            f"collected {len(collected)} ({failures} failures)"
        )
        raise RuntimeError(msg)
    return collected


def augment_evaluation_with_opus(root: Path, *, bitrate: str = "16k") -> None:
    """Add paired, real-Opus validation/test twins to an existing manifest."""
    import imageio_ffmpeg

    manifest = root / "manifest.jsonl"
    if not manifest.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest}")
    records = [
        json.loads(line)
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    source_records = [
        record
        for record in records
        if record.get("split") in {"val", "test"} and record.get("compression_status") == "clean"
    ]
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    compressed: list[dict[str, object]] = []
    for index, record in enumerate(source_records, start=1):
        source = root / str(record["uri"])
        pair_id = str(record["clip_id"])
        record["pair_id"] = pair_id
        output_relative = (
            Path("audio")
            / str(record["language"])
            / f"{record['label']}_opus"
            / f"{pair_id}-opus16.flac"
        )
        output = root / output_relative
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(".opus")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-c:a",
                "libopus",
                "-b:a",
                bitrate,
                "-vbr",
                "on",
                str(temporary),
            ],
            check=True,
        )
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(temporary),
                "-ar",
                str(record["sample_rate_hz"]),
                "-ac",
                "1",
                str(output),
            ],
            check=True,
        )
        temporary.unlink(missing_ok=True)
        twin = dict(record)
        twin["clip_id"] = f"{pair_id}-opus16"
        twin["compression_status"] = "opus_whatsapp_sim"
        twin["uri"] = output_relative.as_posix()
        twin["checksum_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        twin["file_size_bytes"] = output.stat().st_size
        compressed.append(twin)
        if index % 50 == 0:
            print(f"Opus evaluation twins: {index}/{len(source_records)}", flush=True)

    combined = sorted(records + compressed, key=lambda item: str(item["clip_id"]))
    with manifest.open("w", encoding="utf-8") as handle:
        for record in combined:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")

    provenance_path = root / "provenance.json"
    provenance: dict[str, object] = {}
    if provenance_path.is_file():
        raw = json.loads(provenance_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            provenance = raw
    provenance["opus_evaluation"] = {
        "codec": "libopus",
        "bitrate": bitrate,
        "paired_validation_test_twins": len(compressed),
        "decoded_for_model_input": True,
    }
    provenance["total_clips_with_opus_twins"] = len(combined)
    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        f"Added {len(compressed)} paired Opus evaluation clips; total={len(combined)}",
        flush=True,
    )


def main() -> None:
    """Download, normalize, split, and manifest the publication subset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "publication_corpus",
    )
    parser.add_argument("--clips-per-source-language", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--max-duration-sec", type=float, default=12.0)
    parser.add_argument("--shuffle-buffer", type=int, default=1_000)
    parser.add_argument(
        "--augment-existing-opus",
        action="store_true",
        help="Skip downloads and add paired 16 kbps Opus twins to val/test.",
    )
    args = parser.parse_args()

    if args.augment_existing_opus:
        augment_evaluation_with_opus(args.root)
        return

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN is required for gated Kathbath access")
    if args.clips_per_source_language <= 0:
        raise SystemExit("--clips-per-source-language must be positive")

    args.root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for language, (kathbath_config, indicsynth_config) in LANGUAGES.items():
        records.extend(
            _collect_cell(
                rows=_stream_rows(
                    KATHBATH_REPO,
                    kathbath_config,
                    audio_column="audio_filepath",
                    token=token,
                    seed=args.seed,
                    shuffle_buffer=args.shuffle_buffer,
                ),
                root=args.root,
                language=language,
                label="real",
                source="kathbath",
                audio_column="audio_filepath",
                source_name=KATHBATH_REPO,
                speaker_key="speaker_id",
                model_key=None,
                gender_key="gender",
                target_count=args.clips_per_source_language,
                seed=args.seed,
                target_rate=args.sample_rate,
                max_duration_sec=args.max_duration_sec,
            )
        )
        records.extend(
            _collect_cell(
                rows=_stream_rows(
                    INDICSYNTH_REPO,
                    indicsynth_config,
                    audio_column="audio",
                    token=None,
                    seed=args.seed,
                    shuffle_buffer=args.shuffle_buffer,
                ),
                root=args.root,
                language=language,
                label="fake",
                source="indicsynth",
                audio_column="audio",
                source_name=INDICSYNTH_REPO,
                speaker_key="Target Speaker ID",
                model_key="Generative Model",
                gender_key="Gender",
                target_count=args.clips_per_source_language,
                seed=args.seed,
                target_rate=args.sample_rate,
                max_duration_sec=args.max_duration_sec,
            )
        )

    manifest = args.root / "manifest.jsonl"
    with manifest.open("w", encoding="utf-8") as handle:
        for record in sorted(records, key=lambda item: str(item["clip_id"])):
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")

    split_counts = {
        split: sum(1 for record in records if record["split"] == split)
        for split in ("train", "val", "test")
    }
    language_counts = {
        language: sum(1 for record in records if record["language"] == language)
        for language in LANGUAGES
    }
    label_counts = {
        label: sum(1 for record in records if record["label"] == label)
        for label in ("real", "fake")
    }
    unique_speakers = {
        split: len({str(record["speaker_id"]) for record in records if record["split"] == split})
        for split in ("train", "val", "test")
    }
    total_hours = sum(float(record["duration_sec"]) for record in records) / 3_600
    provenance = {
        "created_at": datetime.now(UTC).isoformat(),
        "seed": args.seed,
        "sample_rate_hz": args.sample_rate,
        "max_duration_sec": args.max_duration_sec,
        "clips_per_source_language": args.clips_per_source_language,
        "total_clips": len(records),
        "total_hours": round(total_hours, 4),
        "languages": list(LANGUAGES),
        "language_counts": language_counts,
        "label_counts": label_counts,
        "split_counts": split_counts,
        "unique_speakers_by_split": unique_speakers,
        "split_protocol": (
            "SHA-256(seed:speaker_id), 70/15/15; shared IDs span neither source nor split"
        ),
        "sources": {
            "real": {
                "repository": KATHBATH_REPO,
                "license": "CC0 packaging; source terms accepted by the authenticated user",
            },
            "fake": {
                "repository": INDICSYNTH_REPO,
                "license": "CC BY-NC 4.0; non-commercial academic research",
            },
        },
        "scope_note": (
            "Reproducible bounded subset because the six full target-language cells "
            "exceed 300 GB; results apply only to this persisted subset."
        ),
    }
    (args.root / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(provenance, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
