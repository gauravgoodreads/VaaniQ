#!/usr/bin/env python3
"""Complete V2 manifest with FLEURS real clips; resilient to per-language failures."""

from __future__ import annotations

import json
import os
import shutil
import sys
import traceback
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "scripts"))
sys.path.insert(0, str(_REPO / "backend" / "src"))

from prepare_benchmark_v2 import (  # noqa: E402
    _load_v1_records,
    _rows_for_second_real,
)
from prepare_publication_corpus import (  # noqa: E402
    _collect_cell,
    augment_evaluation_with_opus,
)


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


def _write_manifest(root: Path, records: list[dict[str, object]]) -> dict[str, object]:
    by_id = {str(r["clip_id"]): r for r in records}
    merged = list(by_id.values())
    manifest = root / "manifest.jsonl"
    with manifest.open("w", encoding="utf-8") as fh:
        for rec in sorted(merged, key=lambda item: str(item["clip_id"])):
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    sources = dict(Counter(str(r.get("source")) for r in merged))
    provenance = {
        "benchmark_version": "v2",
        "total_clips": len(merged),
        "source_counts": sources,
        "scope_note": (
            "V2 extends V1 with FLEURS real speech where downloadable; "
            "generator metadata on IndicSynth fakes."
        ),
    }
    (root / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return provenance


def main() -> int:
    _load_dotenv()
    token = os.environ.get("HF_TOKEN")
    root = _REPO / "data" / "benchmark_v2"
    root.mkdir(parents=True, exist_ok=True)
    records = _load_v1_records(_REPO / "data" / "publication_corpus", seed=42)

    src_audio = _REPO / "data" / "publication_corpus" / "audio"
    dst_audio = root / "audio"
    if src_audio.is_dir() and not dst_audio.exists():
        shutil.copytree(src_audio, dst_audio)

    failures: list[str] = []
    for language, cfg in (("hi", "hi_in"), ("mr", "mr_in"), ("ta", "ta_in")):
        have = sum(
            1 for r in records if r.get("source") == "fleurs" and r.get("language") == language
        )
        if have >= 50:
            print(f"skip {language} fleurs already have {have}", flush=True)
            continue
        need = 50 - have
        try:
            rows = _rows_for_second_real(
                "fleurs",
                "google/fleurs",
                cfg,
                "audio",
                token=token,
                seed=44,
                shuffle_buffer=800,
                target_count=need,
            )
            extra = _collect_cell(
                rows=iter(rows),
                root=root,
                language=language,
                label="real",
                source="fleurs",
                audio_column="audio",
                source_name="google/fleurs",
                speaker_key="id",
                model_key=None,
                gender_key="gender",
                target_count=need,
                seed=42,
                target_rate=16_000,
                max_duration_sec=12.0,
            )
            for row in extra:
                row["speaker_id"] = f"fl-{row.get('speaker_id', 'unk')}"
                row["benchmark_version"] = "v2"
                row["source_dataset"] = "fleurs"
                row["codec_condition"] = "clean"
                row["preprocessing_version"] = "v1"
            records.extend(extra)
            print(f"added fleurs {language} n={len(extra)}", flush=True)
            summary = _write_manifest(root, records)
            print(json.dumps(summary, indent=2), flush=True)
        except Exception as exc:
            msg = f"{language}:{type(exc).__name__}:{exc}"
            failures.append(msg)
            print(f"FAILED fleurs {language}: {exc}", flush=True)
            traceback.print_exc()

    summary = _write_manifest(root, records)
    print(json.dumps({"final": summary, "failures": failures}, indent=2), flush=True)

    try:
        augment_evaluation_with_opus(root)
        print("opus augmentation complete", flush=True)
    except Exception as exc:
        print(f"opus augmentation skipped: {exc}", flush=True)

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
