#!/usr/bin/env python3
"""Prepare Benchmark V2: multi-source real + generator-aware fake splits.

Extends Baseline V1 by adding Common Voice real speech and tagging IndicSynth
rows with ``generation_model`` for generator-disjoint evaluation metadata.
Does not replace V1 — writes to ``data/benchmark_v2/`` by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = _REPO / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
sys.path.insert(0, str(_REPO / "backend" / "src"))

# Reuse V1 helpers
sys.path.insert(0, str(_REPO / "scripts"))
from prepare_publication_corpus import (  # noqa: E402
    INDICSYNTH_REPO,
    KATHBATH_REPO,
    LANGUAGES,
    _collect_cell,
    _stream_rows,
    augment_evaluation_with_opus,
    speaker_split,
)

COMMON_VOICE_REPO = "mozilla-foundation/common_voice_17_0"
INDICVOICES_REPO = "ai4bharat/indicvoices_r"
FLEURS_REPO = "google/fleurs"
CV_CONFIGS = {"hi": "hi", "mr": "mr", "ta": "ta"}
IVR_CONFIGS = {"hi": "hindi", "mr": "marathi", "ta": "tamil"}
FLEURS_CONFIGS = {"hi": "hi_in", "mr": "mr_in", "ta": "ta_in"}


def _stream_rows_fleurs(
    config: str,
    *,
    token: str | None,
    seed: int,
    max_rows: int,
) -> list[dict[str, object]]:
    """Load a bounded FLEURS slice (non-streaming) for faster V2 ingest."""
    from datasets import Audio, load_dataset

    take = min(max_rows, 500)
    dataset = load_dataset(
        FLEURS_REPO,
        config,
        split=f"train[:{take}]",
        token=token,
    )
    dataset = dataset.cast_column("audio", Audio(decode=False))
    dataset = dataset.shuffle(seed=seed)
    return [dict(row) for row in dataset]


def _rows_for_second_real(
    source_name: str,
    repo: str,
    cfg: str,
    audio_col: str,
    *,
    token: str | None,
    seed: int,
    shuffle_buffer: int,
    target_count: int,
) -> list[dict[str, object]]:
    """Return iterable rows for an independent real-speech source."""
    if source_name == "fleurs":
        return _stream_rows_fleurs(cfg, token=token, seed=seed, max_rows=target_count * 4)
    return list(
        _stream_rows(
            repo,
            cfg,
            audio_column=audio_col,
            token=token,
            seed=seed,
            shuffle_buffer=shuffle_buffer,
        )
    )

def _assign_generator_disjoint_split(model_name: str, *, seed: int) -> str:
    """Hold out ~30% of generators for test via deterministic hash."""
    digest = hashlib.sha256(f"{seed}:gen:{model_name}".encode()).digest()
    bucket = int.from_bytes(digest[:4], "big") % 10_000
    return "test" if bucket >= 7_000 else "train"


def _load_v1_records(v1_root: Path, *, seed: int) -> list[dict[str, object]]:
    manifest = v1_root / "manifest.jsonl"
    if not manifest.is_file():
        return []
    rows: list[dict[str, object]] = []
    with manifest.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    for row in rows:
        row["benchmark_version"] = "v1_import"
        row.setdefault("source_dataset", str(row.get("source", "unknown")))
        row.setdefault("codec_condition", str(row.get("compression_status", "clean")))
        row.setdefault("preprocessing_version", "v1")
        if row.get("label") == "fake" and row.get("generation_model"):
            gen = str(row["generation_model"])
            row["generator_name"] = gen
            row["generator_disjoint_bucket"] = _assign_generator_disjoint_split(
                gen, seed=seed
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=_REPO / "data" / "benchmark_v2",
    )
    parser.add_argument(
        "--import-v1-from",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
        help="Copy V1 manifest rows into V2 (preserved unchanged).",
    )
    parser.add_argument("--clips-per-cv-language", type=int, default=80)
    parser.add_argument("--clips-per-kathbath-language", type=int, default=150)
    parser.add_argument("--clips-per-indicsynth-language", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--max-duration-sec", type=float, default=12.0)
    parser.add_argument("--shuffle-buffer", type=int, default=800)
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Only merge existing V1 + write protocol metadata (no HF).",
    )
    parser.add_argument(
        "--cv-only-addition",
        action="store_true",
        help="When importing V1, only stream Common Voice real clips (skip re-downloading Kathbath/IndicSynth).",
    )
    parser.add_argument(
        "--second-real-source",
        choices=("common_voice", "indicvoices_r", "fleurs", "auto"),
        default="auto",
        help="Independent real-speech source (auto tries IndicVoices-R, FLEURS, then CV).",
    )
    parser.add_argument(
        "--augment-opus",
        action="store_true",
        help="Add paired 16 kbps Opus twins for val/test after build.",
    )
    args = parser.parse_args()
    _load_dotenv()

    args.root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    if args.import_v1_from.is_dir():
        v1_rows = _load_v1_records(args.import_v1_from, seed=args.seed)
        if v1_rows:
            # Symlink/copy audio tree
            src_audio = args.import_v1_from / "audio"
            dst_audio = args.root / "audio"
            if src_audio.is_dir() and not dst_audio.exists():
                shutil.copytree(src_audio, dst_audio)
            records.extend(v1_rows)

    if not args.skip_download:
        token = os.environ.get("HF_TOKEN")
        if not token:
            raise SystemExit("HF_TOKEN required for Kathbath/Common Voice unless --skip-download")

        for language, (kathbath_config, indicsynth_config) in LANGUAGES.items():
            if not args.cv_only_addition:
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
                        target_count=args.clips_per_kathbath_language,
                        seed=args.seed,
                        target_rate=args.sample_rate,
                        max_duration_sec=args.max_duration_sec,
                    )
                )
            second_source = args.second_real_source
            ivr_config = IVR_CONFIGS.get(language)
            if args.cv_only_addition and ivr_config:
                sources_to_try: list[tuple[str, str, str, str, str]] = []
                if second_source in ("auto", "indicvoices_r"):
                    sources_to_try.append(
                        (
                            "indicvoices_r",
                            INDICVOICES_REPO,
                            ivr_config,
                            "audio",
                            "speaker_id",
                        )
                    )
                if second_source in ("auto", "fleurs"):
                    fleurs_config = FLEURS_CONFIGS.get(language)
                    if fleurs_config:
                        sources_to_try.append(
                            (
                                "fleurs",
                                FLEURS_REPO,
                                fleurs_config,
                                "audio",
                                "id",
                            )
                        )
                if second_source in ("auto", "common_voice"):
                    cv_config = CV_CONFIGS.get(language)
                    if cv_config:
                        sources_to_try.append(
                            (
                                "common_voice",
                                COMMON_VOICE_REPO,
                                cv_config,
                                "audio",
                                "client_id",
                            )
                        )
                for src_name, repo, cfg, audio_col, spk_key in sources_to_try:
                    try:
                        row_iter = _rows_for_second_real(
                            src_name,
                            repo,
                            cfg,
                            audio_col,
                            token=token,
                            seed=args.seed + 2,
                            shuffle_buffer=args.shuffle_buffer,
                            target_count=args.clips_per_cv_language,
                        )
                        extra_rows = _collect_cell(
                            rows=iter(row_iter),
                            root=args.root,
                            language=language,
                            label="real",
                            source=src_name,
                            audio_column=audio_col,
                            source_name=repo,
                            speaker_key=spk_key,
                            model_key=None,
                            gender_key="gender",
                            target_count=args.clips_per_cv_language,
                            seed=args.seed,
                            target_rate=args.sample_rate,
                            max_duration_sec=args.max_duration_sec,
                        )
                        for row in extra_rows:
                            spk = str(row.get("speaker_id", "unknown"))
                            row["speaker_id"] = f"{src_name[:2]}-{spk}"
                            row["benchmark_version"] = "v2"
                            row["evaluation_protocol"] = "multi_source_real"
                            row["source_dataset"] = src_name
                            row["source_clip_id"] = row.get("clip_id")
                            row["codec_condition"] = "clean"
                            row["preprocessing_version"] = "v1"
                        records.extend(extra_rows)
                        print(f"added_second_real source={src_name} lang={language} n={len(extra_rows)}", flush=True)
                        break
                    except Exception as exc:
                        print(f"second_real_source_failed source={src_name} lang={language} err={exc}")
                        continue

            if args.cv_only_addition:
                continue

            fake_rows = _collect_cell(
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
                target_count=args.clips_per_indicsynth_language,
                seed=args.seed,
                target_rate=args.sample_rate,
                max_duration_sec=args.max_duration_sec,
            )
            for row in fake_rows:
                gen = str(row.get("generation_model") or "unknown")
                row["generator_disjoint_bucket"] = _assign_generator_disjoint_split(
                    gen, seed=args.seed
                )
                row["benchmark_version"] = "v2"
            records.extend(fake_rows)

    # Deduplicate by clip_id (V1 import may overlap if re-downloaded)
    by_id: dict[str, dict[str, object]] = {}
    for row in records:
        by_id[str(row["clip_id"])] = row
    records = list(by_id.values())

    manifest = args.root / "manifest.jsonl"
    with manifest.open("w", encoding="utf-8") as handle:
        for record in sorted(records, key=lambda item: str(item["clip_id"])):
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")

    sources = Counter(str(r.get("source")) for r in records)
    generators = Counter(str(r.get("generation_model") or "n/a") for r in records if r.get("label") == "fake")
    provenance = {
        "benchmark_version": "v2",
        "created_at": datetime.now(UTC).isoformat(),
        "seed": args.seed,
        "total_clips": len(records),
        "source_counts": dict(sources),
        "fake_generators": dict(generators),
        "evaluation_protocols": {
            "speaker_disjoint": "SHA-256(seed:speaker_id) 70/15/15",
            "source_disjoint_eval": (
                "Train real may include Kathbath; held-out FLEURS/Common Voice real "
                "reserved for source-disjoint test cells when enabled in eval script."
            ),
            "generator_disjoint_eval": (
                "IndicSynth rows tagged with generator_disjoint_bucket via "
                "SHA-256(seed:gen:model_name)."
            ),
        },
        "v1_preserved_at": str(args.import_v1_from),
        "scope_note": (
            "V2 reduces source-label confounding vs V1 by adding independent real "
            "Common Voice and generator metadata; not a full-corpus claim."
        ),
        "licences": {
            "kathbath": "gated; authenticated user terms",
            "common_voice": "CC0 / CV licence per Mozilla",
            "fleurs": "CC BY 4.0 (Google FLEURS)",
            "indicsynth": "CC BY-NC 4.0",
        },
    }
    (args.root / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.augment_opus:
        augment_evaluation_with_opus(args.root)

    print(json.dumps(provenance, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
