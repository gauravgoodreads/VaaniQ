#!/usr/bin/env python3
"""Extract and cache frozen XLS-R embeddings for a corpus manifest."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import soundfile as sf

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.audio.transforms.preprocessor import DefaultPreprocessor
from vaaniq.config.domains import XlsrAasistConfig
from vaaniq.core.domain.entities import Waveform
from vaaniq.features.cache.filesystem import FilesystemEmbeddingCache
from vaaniq.features.xlsr.extractor import FrozenXLSRExtractor


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=_REPO / "data" / "embedding_cache" / "xlsr_300m",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max clips (0=all)")
    parser.add_argument(
        "--use-cpu",
        action="store_true",
        help="Force CPU inference (slower but works without CUDA).",
    )
    args = parser.parse_args()
    _load_dotenv()

    if args.use_cpu:
        import os

        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    manifest = args.corpus / "manifest.jsonl"
    rows: list[dict[str, object]] = []
    with manifest.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    if args.limit > 0:
        rows = rows[: args.limit]

    cache = FilesystemEmbeddingCache(args.cache_root)
    config = XlsrAasistConfig()
    extractor = FrozenXLSRExtractor(config=config, cache=cache)
    pre = DefaultPreprocessor()

    n_ok = 0
    n_fail = 0
    for row in rows:
        clip_id = str(row.get("clip_id", "unknown"))
        path = args.corpus / str(row.get("uri", ""))
        if not path.is_file():
            n_fail += 1
            continue
        data, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if getattr(data, "ndim", 1) > 1:
            import numpy as np

            data = np.mean(data, axis=1)
        wav = pre.transform(Waveform(samples=data, sample_rate_hz=int(sr)))
        try:
            extractor.extract(wav, clip_id=clip_id)
            n_ok += 1
            if n_ok % 50 == 0:
                print(f"cached={n_ok} failed={n_fail}")
        except Exception as exc:  # noqa: BLE001 — batch job continues
            print(f"fail clip_id={clip_id} error={exc}")
            n_fail += 1

    summary = {
        "model_id": config.xlsr_model_id,
        "cache_root": str(args.cache_root),
        "n_cached": n_ok,
        "n_failed": n_fail,
        "corpus": str(args.corpus),
    }
    args.cache_root.mkdir(parents=True, exist_ok=True)
    (args.cache_root / "extraction_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0 if n_ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
